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

import re

from oslo_log import log as logging

from os_brick import initiator

from os_brick.initiator.connectors import base
from os_brick import utils

DEVICE_SCAN_ATTEMPTS_DEFAULT = 3
LOG = logging.getLogger(__name__)


class NVMeConnector(base.BaseLinuxConnector):
    """Connector class to attach/detach NVMe over fabric volumes."""

    def __init__(self, root_helper, driver=None,
                 device_scan_attempts=initiator.DEVICE_SCAN_ATTEMPTS_DEFAULT,
                 *args, **kwargs):
        super(NVMeConnector, self).__init__(
            root_helper,
            driver=driver,
            device_scan_attempts=device_scan_attempts,
            *args, **kwargs)

    @staticmethod
    def get_connector_properties(root_helper, *args, **kwargs):
        """The NVMe connector properties."""
        return {}

    def get_search_path(self):
        return '/dev  '

    def get_volume_paths(self, connection_properties):
        raise NotImplementedError

    def _get_nvme_portals_from_output(self, output):
        # TODO(e0ne): replace with better regexp
        pattern = r'subnqn:(.*)'
        for line in output.split('\n'):
            result = re.match(pattern, line)
            if result:
                return result.group(1).strip()

    def _discover_nvme_portals(self, connection_properties):
        target_portal = connection_properties['target_portal']
        port = connection_properties['target_port']
        cmd = ['/usr/local/sbin/nvme', 'discover', '-t' 'rdma',
               '-a', target_portal, '-s', port]
        (out, err) = self._execute(*cmd, root_helper=self._root_helper,
                                   run_as_root=True)
        return self._get_nvme_portals_from_output(out)

    def _get_nvme_devices(self):
        nvme_devices = []
        pattern = r'/dev/nvme[0-9]n[0-9]'
        cmd = ['/usr/local/sbin/nvme', 'list']
        (out, err) = self._execute(*cmd, root_helper=self._root_helper,
                                   run_as_root=True)
        for line in out.split('\n'):
            result = re.match(pattern, line)
            if result:
                nvme_devices.append(result.group(0))

        return nvme_devices

    # TODO(e0ne): add lock
    @utils.trace
    def connect_volume(self, connection_properties):
        """Discover and attach the volume.

        :param connection_properties: The dictionary that describes all
                                      of the target volume attributes.
        :type connection_properties: dict
        :returns: dict

        connection_properties for NVMe must include:
        TODO (e0ne): add connection_properties description
        """

        current_nvme_devices = self._get_nvme_devices()

        device_info = {'type': 'block'}
        nqn = connection_properties['nqn']
        self._discover_nvme_portals(connection_properties)
        target_portal = connection_properties['target_portal']
        port = connection_properties['target_port']
        cmd = ['/usr/local/sbin/nvme', 'connect', '-t', 'rdma', '-n', nqn,
               '-a', target_portal, '-s', port]

        self._execute(*cmd, root_helper=self._root_helper,
                      run_as_root=True)
        # TODO(e0ne): find more propper solution for it once
        # PoC is implemented
        # TODO (e0ne): fixme
        import time; time.sleep(2)
        all_nvme_devices = self._get_nvme_devices()
        path = set(all_nvme_devices) - set(current_nvme_devices)
        path = list(path)
        device_info['path'] = path[0]

        return device_info

    # TODO(e0ne): add lock
    @utils.trace
    def disconnect_volume(self, connection_properties, device_info):
        """Detach and flush the volume.

        :param connection_properties: The dictionary that describes all
                                      of the target volume attributes.
        :type connection_properties: dict
        :param device_info: historical difference, but same as connection_props
        :type device_info: dict

        connection_properties for NVMe must include:
        TODO (e0ne): add connection_properties description
        """
        nqn = self._discover_nvme_portals(connection_properties)
        # TODO(e0ne): clarify command with manual
        # NOTE(e0ne): temporaty fix until disconnect via nqn will be implemented
        if 'device_path' in connection_properties:
            device_name = connection_properties['device_path'].split('/')[-1]
            cmd = ['/usr/local/sbin/nvme', 'disconnect', '-d', device_name]
        else:
            cmd = ['/usr/local/sbin/nvme', 'disconnect', '-n', nqn]
        self._execute(*cmd, root_helper=self._root_helper, run_as_root=True)

    def extend_volume(self, connection_properties):
        # TODO(e0ne): is this possible?
        raise NotImplementedError
