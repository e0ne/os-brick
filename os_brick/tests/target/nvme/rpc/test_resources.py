# All Rights Reserved.
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

from os_brick import exception
from os_brick.target.nvme.rpc import resources
from os_brick.tests import base


class NVMeTargetObjectTestCase(base.TestCase):

    def setUp(self):
        super(NVMeTargetObjectTestCase, self).setUp()
        self.nvme_target_objects = resources.NVMeTargetObject()
        self.client_mock = self.mock_object(self.nvme_target_objects, 'client')

    def test_get_initiator_groups(self):
        self.nvme_target_objects.get_initiator_groups()
        self.client_mock.call.assert_called_once_with('get_initiator_groups')

    def test_add_initiator_group(self):
        self.nvme_target_objects.add_initiator_group(
            1, ['127.0.0.1'], ['255.255.0.0']
        )
        self.client_mock.call.assert_called_once_with(
            'add_initiator_group',
            {
                'tag': 1,
                'initiators': ['127.0.0.1'],
                'netmasks': ['255.255.0.0']
            }
        )

    def test_add_initiator_group_with_wrong_tag(self):
        with self.assertRaisesRegexp(exception.NVMeParamException,
                                     'Tag value must be > 0'):
            self.nvme_target_objects.add_initiator_group(
                0, ['127.0.0.1'], ['255.255.0.0']
            )

    def test_delete_initiator_group(self):
        self.nvme_target_objects.delete_initiator_group(2)
        self.client_mock.call.assert_called_once_with('delete_initiator_group',
                                                      {'tag': 2})

    def test_delete_initiator_group_with_wrong_tag(self):
        with self.assertRaisesRegexp(exception.NVMeParamException,
                                     'Tag value must be > 0'):
            self.nvme_target_objects.delete_initiator_group(-1)

    def test_get_portal_groups(self):
        self.nvme_target_objects.get_portal_groups()
        self.client_mock.call.assert_called_once_with('get_portal_groups')

    def test_add_portal_group(self):
        self.nvme_target_objects.add_portal_group(
            3, ['192.168.100.100:3260', '192.168.100.100:3261'])
        self.client_mock.call.assert_called_once_with(
            'add_portal_group',
            {
                'tag': 3,
                'portals': ['192.168.100.100:3260', '192.168.100.100:3261']
            }
        )

    def test_add_portal_group_with_wrong_tag(self):
        with self.assertRaisesRegexp(exception.NVMeParamException,
                                     'Tag value must be > 0'):
            self.nvme_target_objects.add_portal_group(-2, ['192.168.1.1:3260'])

    def test_delete_portal_group(self):
        self.nvme_target_objects.delete_portal_group(4)
        self.client_mock.call.assert_called_once_with('delete_portal_group',
                                                      {'tag': 4})

    def test_delete_portal_group_with_wrong_tag(self):
        with self.assertRaisesRegexp(exception.NVMeParamException,
                                     'Tag value must be > 0'):
            self.nvme_target_objects.delete_portal_group(0)

    def test_get_target_nodes(self):
        self.nvme_target_objects.get_target_nodes()
        self.client_mock.call.assert_called_once_with('get_target_nodes')

    def test_add_target_node(self):
        self.nvme_target_objects.add_target_node(
            'target_name', 'target_alias', [1, 2], [10, 20],
            ['Malloc0', 'Malloc1'], [0, 1], 64, 0, 0, 1, 1)
        self.client_mock.call.assert_called_once_with(
            'construct_target_node',
            {
                'name': 'target_name',
                'alias_name': 'target_alias',
                'pg_tags': [1, 2],
                'ig_tags': [10, 20],
                'lun_names': ['Malloc0', 'Malloc1'],
                'lun_ids': [0, 1],
                'queue_depth': 64,
                'chap_disabled': 0,
                'chap_required': 0,
                'chap_mutual': 1,
                'chap_auth_group': 1
            }
        )

    def test_add_target_node_with_wrong_pg_iq_tags(self):
        with self.assertRaisesRegexp(exception.NVMeParamException,
                                     'Tag value must be > 0'):
            self.nvme_target_objects.add_target_node(
                'target_name', 'target_alias', [-1, 2], [10, 20],
                ['Malloc0', 'Malloc1'], [0, 1], 64, 0, 0, 1, 1)

        with self.assertRaisesRegexp(exception.NVMeParamException,
                                     'Tag value must be > 0'):
            self.nvme_target_objects.add_target_node(
                'target_name', 'target_alias', [1, 2], [0, 20],
                ['Malloc0', 'Malloc1'], [0, 1], 64, 0, 0, 1, 1)

    def test_add_target_node_with_wrong_lun0_ids(self):
        with self.assertRaisesRegexp(exception.NVMeParamException,
                                     'LUN0 \(\id \= 0\)\ is required'):
            self.nvme_target_objects.add_target_node(
                'target_name', 'target_alias', [1, 2], [10, 20],
                ['Malloc-1', 'Malloc1'], [-1, 1], 64, 0, 0, 1, 1)

    def test_delete_target_node(self):
        self.nvme_target_objects.delete_target_node('iqn.2016-06.io.spdk:disk')
        self.client_mock.call.assert_called_once_with(
            'delete_target_node', {'name': 'iqn.2016-06.io.spdk:disk'})

    def test_get_active_luns(self):
        self.nvme_target_objects.get_active_luns()
        self.client_mock.call.assert_called_once_with('get_luns')

    def test_delete_lun(self):
        self.nvme_target_objects.delete_lun('Malloc0')
        self.client_mock.call.assert_called_once_with(
            'delete_lun', {'name': 'Malloc0'})

    def test_construct_aio_lun(self):
        self.nvme_target_objects.construct_aio_lun('/dev/sda')
        self.client_mock.call.assert_called_once_with(
            'construct_aio_lun', {'fname': '/dev/sda'})

    def test_construct_malloc_lun(self):
        self.nvme_target_objects.construct_malloc_lun(64, 512)
        self.client_mock.call.assert_called_once_with(
            'construct_malloc_lun', {'num_blocks': 131072, 'block_size': 512}
        )

    def test_construct_malloc_lun_with_wrong_total_size(self):
        for total_size in (0, -32):
            with self.assertRaisesRegexp(exception.NVMeParamException,
                                         'Total size must be > 0'):
                self.nvme_target_objects.construct_malloc_lun(total_size, 512)

    def test_construct_malloc_lun_with_wrong_block_size(self):
        for block_size in (0, -512):
            with self.assertRaisesRegexp(exception.NVMeParamException,
                                         'Block size must be > 0'):
                self.nvme_target_objects.construct_malloc_lun(32, block_size)

    def test_add_ip_address(self):
        self.nvme_target_objects.add_ip_address(1, 'localhost')
        self.client_mock.call.assert_called_once_with(
            'add_ip_address', {'ifc_index': 1, 'ip_address': 'localhost'}
        )

    def test_delete_ip_address(self):
        self.nvme_target_objects.delete_ip_address(1, 'localhost')
        self.client_mock.call.assert_called_once_with(
            'delete_ip_address', {'ifc_index': 1, 'ip_address': 'localhost'}
        )

    def test_get_trace_flags(self):
        self.nvme_target_objects.get_trace_flags()
        self.client_mock.call.assert_called_once_with('get_trace_flags')

    def test_set_trace_flag(self):
        self.nvme_target_objects.set_trace_flag('debug')
        self.client_mock.call.assert_called_once_with(
            'set_trace_flag', {'flag': 'debug'})

    def test_clear_trace_flag(self):
        self.nvme_target_objects.clear_trace_flag('debug')
        self.client_mock.call.assert_called_once_with(
            'clear_trace_flag', {'flag': 'debug'})

    def test_get_interfaces(self):
        self.nvme_target_objects.get_interfaces()
        self.client_mock.call.assert_called_once_with('get_interfaces')

    def delete_nvmf_subsystem(self):
        self.nvme_target_objects.get_iscsi_connections()
        self.client_mock.call.assert_called_once_with('get_iscsi_connections')

    def test_get_scsi_devices(self):
        self.nvme_target_objects.get_scsi_devices()
        self.client_mock.call.assert_called_once_with('get_scsi_devices')

    def test_construct_nvmf_subsystem(self):
        self.nvme_target_objects.construct_nvmf_subsystem(
            'target_name', 'target_alias', [1, 2], [10, 20],
            ['Malloc0', 'Malloc1'], [0, 1], 64, 0, 0, 1, 1)
        self.client_mock.call.assert_called_once_with(
            'construct_nvmf_subsystem',
            {
                'name': 'target_name',
                'alias_name': 'target_alias',
                'pg_tags': [1, 2],
                'ig_tags': [10, 20],
                'lun_names': ['Malloc0', 'Malloc1'],
                'lun_ids': [0, 1],
                'queue_depth': 64,
                'chap_disabled': 0,
                'chap_required': 0,
                'chap_mutual': 1,
                'chap_auth_group': 1
            }
        )

    def delete_nvmf_subsystem(self):
        pass

    def get_nvmf_subsystems(self):
        pass

    def test_kill(self):
        self.nvme_target_objects.kill('SIGTERM')
        self.client_mock.call.assert_called_once_with(
            'kill_instance', {'sig_name': 'SIGTERM'})
