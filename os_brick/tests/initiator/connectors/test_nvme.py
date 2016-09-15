# (c) Copyright 2013 Hewlett-Packard Development Company, L.P.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import mock

from os_brick.initiator.connectors import nvme
from os_brick.tests.initiator import test_connector


FAKE_NVME_DISCOVER_OUTPUT = """
Discovery Log Number of Records 1, Generation counter 1
=====Discovery Log Entry 0======
trtype:  ipv4
adrfam:  unknown
nqntype: 2
treq:    0
portid:  1
trsvcid: 1023

subnqn:  nvme-subsystem-name
traddr:  11.212.7.13

rdma_prtype: 0
rdma_qptype: 0
rdma_cms:    0
rdma_pkey: 0x0000
"""

FAKE_NVME_LIST_OUTPUT = """
Node             Model                Version  Namepace Usage                      Format           FW Rev  
---------------- -------------------- -------- -------- -------------------------- ---------------- --------
/dev/nvme0n1     Vendor SSD 950 PRO   1.1      1         62.44  GB / 256.06  GB    512   B +  0 B   XXXXXXXX

"""


class NVMeConnectorTestCase(test_connector.ConnectorTestCase):
    """Test cases for AoE initiator class."""

    def setUp(self):
        super(NVMeConnectorTestCase, self).setUp()
        self.connector = nvme.NVMeConnector(None,
                                            execute=self.fake_execute)
        self.connection_properties = {'target_shelf': 'fake_shelf',
                                      'target_lun': 'fake_lun'}

    def test__get_nvme_portals_from_output(self):
        expected = "nvme-subsystem-name"
        actual_nqn = self.connector._get_nvme_portals_from_output(
            FAKE_NVME_DISCOVER_OUTPUT)
        self.assertEqual(expected, actual_nqn)

    def _nvme_list_cmd(self, *args, **kwargs):
        return FAKE_NVME_LIST_OUTPUT, None

    def test__get_nvme_devices(self):
        expected = ['/dev/nvme0n1']
        self.connector._execute = self._nvme_list_cmd
        actual = self.connector._get_nvme_devices()
        self.assertEqual(expected, actual)

    @mock.patch.object(nvme.NVMeConnector, '_get_nvme_devices')
    @mock.patch.object(nvme.NVMeConnector, '_discover_nvme_portals')
    @mock.patch.object(nvme.NVMeConnector, '_execute')
    def test_connect_volume(self, mock_execute, mock_discover, mock_devices):
        connection_properties = {'target_portal': 'portal',
                                 'target_port': 1}

        mock_discover.return_value = 'nqn'
        mock_devices.side_effect = [['/dev/nvme0n1'], ['/dev/nvme0n2']]

        device_info = self.connector.connect_volume(connection_properties)
        self.assertEqual('/dev/nvme0n2', device_info['path'])
        self.assertEqual('block', device_info['type'])

        mock_discover.assert_called_once_with(connection_properties)
        self.assertEqual(2, mock_devices.call_count)

        mock_execute.assert_called_once_with('nvme', 'connect', '-t',
                                             'rdma', '-n', 'nqn',
                                             '-a', 'portal', '-s', 1,
                                             root_helper=None,
                                             run_as_root=True)

    @mock.patch.object(nvme.NVMeConnector, '_discover_nvme_portals')
    @mock.patch.object(nvme.NVMeConnector, '_execute')
    def test_disconnect_volume(self, mock_execute, mock_discover):
        mock_discover.return_value = 'nqn'
        connection_properties = {'target_portal': 'portal',
                                 'target_port': 1}
        self.connector.disconnect_volume(connection_properties, None)

        mock_discover.assert_called_once_with(connection_properties)
        mock_execute.asert_called_once_with('nvme', 'disconnect', '-n', 'nqn',
                                            root_helper=None,
                                            run_as_root=True)
