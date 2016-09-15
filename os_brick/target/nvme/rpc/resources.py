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
from os_brick.target.nvme import client


class NVMeTargetObject(object):

    def __init__(self, ip_address='127.0.0.1', port=4420,):
        self.client = client.NVMeRPCClient(ip_address, port)

    def get_initiator_groups(self):
        """Display current initiator group configuration.

        :returns: dict
        """

        return self.client.call('get_initiator_groups')

    def add_initiator_group(self, tag, initiators, netmasks):
        """Add an initiator group.

        :param tag: initiator group tag
        :type tag: int
        :param initiators: list of initiator hostnames or IP addresses,
                           enclosed in quotes.  Example: ['ALL'] or
                           ['127.0.0.1', '192.168.200.100'].
        :type initiators: list of strings
        :param netmasks: list of initiator netmasks enclosed in quotes.
                         Example: ['255.255.0.0', '255.248.0.0'].
        :type netmasks: list of strings
        :returns: None
        """

        if not (tag > 0):
            raise exception.NVMeParamException(
                validation_message='Tag value must be > 0')

        return self.client.call(
            'add_initiator_group', {
                'tag': tag,
                'initiators': initiators,
                'netmasks': netmasks
            })

    def delete_initiator_group(self, tag):
        """Delete an initiator group.

        :param tag: initiator group tag
        :type tag: int
        :returns: None
        """

        if not (tag > 0):
            raise exception.NVMeParamException(
                validation_message='Tag value must be > 0')

        return self.client.call('delete_initiator_group', {'tag': tag})

    def get_portal_groups(self):
        """Display current portal group configuration.

        :returns: dict
        """

        return self.client.call('get_portal_groups')

    def add_portal_group(self, tag, portals):
        """Add a portal group.

        :param tag: portal group tag
        :type tag: int
        :param portals: list of portals in 'host:port' format. Example:
                        ['192.168.100.100:3260', '192.168.100.100:3261']
        :type portals: list of strings
        :returns: None
        """

        if not (tag > 0):
            raise exception.NVMeParamException(
                validation_message='Tag value must be > 0')

        return self.client.call(
            'add_portal_group', {
                'tag': tag,
                'portals': portals
            })

    def delete_portal_group(self, tag):
        """Delete a portal group.

        :param tag: portal group tag
        :type tag: int
        :returns: None
        """

        if not (tag > 0):
            raise exception.NVMeParamException(
                validation_message='Tag value must be > 0')

        return self.client.call('delete_portal_group', {'tag': tag})

    def get_target_nodes(self):
        """Display target nodes.

        :returns: dict
        """

        return self.client.call('get_target_nodes')

    def add_target_node(self, name, alias_name, pg_tags, ig_tags, lun_names,
                        lun_ids, queue_depth, chap_disabled, chap_required,
                        chap_mutual, chap_auth_group):
        """Add a target node.

        :param name: target node name (ASCII).
        :type name: string
        :param alias_name: target node alias name (ASCII).
        :type alias_name: string
        :param pg_tags: list of Portal Group Tags (int > 0).
        :type pg_tags: list of ints. Portal groups must pre-exist.
        :param ig_tags: list of Initiator Group Tag (int > 0).
        :type ig_tags: list of ints. Initiator group must pre-exist.
        :param lun_names: list of LUNs names. The LUNs must pre-exist.
        :type lun_names: list of strings.
        :param lun_ids: list of LUNs names. The LUNs must pre-exist.
        :type lun_ids: list of ints. LUN0 (id = 0) is required
        :param queue_depth: Desired target queue depth.
        :type queue_depth: int
        :param chap_disabled: CHAP authentication should be disabled for this
                              target node. Mutually exclusive with
                              chap_required.
        :type chap_disabled: int
        :param chap_required: CHAP authentication should be required for this
                              target node. Mutually exclusive with
                              chap_disabled.
        :type chap_required: int
        :param chap_mutual: CHAP authentication should be mutual/bidirectional.
        :type chap_mutual: int
        :param chap_auth_group: Authentication group ID for this target node.
                                Authentication group must be precreated.
        :type chap_auth_group: int
        """

        for tag in pg_tags + ig_tags:
            if not (tag > 0):
                raise exception.NVMeParamException(
                    validation_message='Tag value must be > 0')

        if 0 not in lun_ids:
            raise exception.NVMeParamException(
                validation_message='LUN0 (id = 0) is required')
        # TODO(apopovych): add more validation

        return self.client.call(
            'construct_target_node', {
                'name': name,
                'alias_name': alias_name,
                'pg_tags': pg_tags,
                'ig_tags': ig_tags,
                'lun_names': lun_names,
                'lun_ids': lun_ids,
                'queue_depth': queue_depth,
                'chap_disabled': chap_disabled,
                'chap_required': chap_required,
                'chap_mutual': chap_mutual,
                'chap_auth_group': chap_auth_group,
            })

    def delete_target_node(self, target_node_name):
        """Delete a target node.

        :param target_node_name: target node name to be deleted.
                                 Example: iqn.2016-06.io.spdk:disk1
        :type target_node_name: string
        :returns: None
        """

        return self.client.call(
            'delete_target_node', {
                'name': target_node_name
            })

    def get_active_luns(self):
        """Display active LUNs.

        :returns: dict
        """

        return self.client.call('get_luns')

    def delete_lun(self, lun_name):
        """Delete a LUN.

        :param lun_name: LUN name to be deleted. Example: Malloc0
        :type lun_name: string
        :returns: None
        """

        return self.client.call('delete_lun', {'name': lun_name})

    def construct_aio_lun(self, fname):
        """Add a LUN with aio backend.

        :param fname: path to device or file (ex: /dev/sda)
        :type fname: string
        :returns: None
        """

        return self.client.call('construct_aio_lun', {'fname': fname})

    def construct_malloc_lun(self, total_size, block_size):
        """Add a LUN with malloc backend.

        :param total_size: size of malloc LUN in MB (int > 0).
        :type total_size: int
        :param block_size: block size for this LUN.
        :type block_size: int
        :returns: None
        """

        if not (total_size > 0):
            raise exception.NVMeParamException(
                validation_message='Total size must be > 0')

        if not (block_size > 0):
            raise exception.NVMeParamException(
                validation_message='Block size must be > 0')

        num_blocks = (total_size * 1024 * 1024) / block_size

        return self.client.call(
            'construct_malloc_lun', {
                'num_blocks': num_blocks,
                'block_size': block_size
            })

    def add_ip_address(self, ifc_index, ip_address):
        """Add IP address.

        :param ifc_index: fc index of the nic device.
        :type ifc_index: int
        :param ip_address: ip address will be added.
        :type ip_address: string
        :returns: None
        """

        return self.client.call(
            'add_ip_address', {
                'ifc_index': ifc_index,
                'ip_address': ip_address
            })

    def delete_ip_address(self, ifc_index, ip_address):
        """Delete IP address.

        :param ifc_index: fc index of the nic device.
        :type ifc_index: int
        :param ip_address: ip address will be deleted.
        :type ip_address: string
        :returns: None
        """

        return self.client.call(
            'delete_ip_address', {
                'ifc_index': ifc_index,
                'ip_address': ip_address
            })

    def get_trace_flags(self):
        """Get trace flags.

        :returns: dict
        """

        return self.client.call('get_trace_flags')

    def set_trace_flag(self, flag):
        """Set trace flag.

        :param flag: trace mask we want to set. (for example "debug").
        :type flag: string
        :returns: None
        """

        return self.client.call('set_trace_flag', {'flag': flag})

    def clear_trace_flag(self, flag):
        """Clear trace flag.

        :param flag: trace mask we want to clear. (for example "debug").
        :type flag: string
        :returns: None
        """

        return self.client.call('clear_trace_flag', {'flag': flag})

    def get_interfaces(self):
        """Display current interface list.

        :returns: dict
        """

        return self.client.call('get_interfaces')

    def get_iscsi_connections(self):
        """Display iSCSI connections.

        :returns: dict
        """

        return self.client.call('get_iscsi_connections')

    def get_scsi_devices(self):
        """Display SCSI devices.

        :returns: dict
        """

        return self.client.call('get_scsi_devices')

    def construct_nvmf_subsystem(self, core, mode, nqn, listen_addresses, hosts,
                                 pci_address, serial_number, namespaces):
        """Add a nvmf subsystem.

        :param core: The core Nvmf target run on.
        :type core: int
        :param mode: Target mode: Virtual or Direct.
        :type mode: string
        :param nqn: Target nqn(ASCII).
        :type nqn: string
        :param listen_addresses: List of Listen pairs. Example:
                                 [{'transport’: ‘RDMA’,
                                   ‘traddr’: ‘192.168.100.8’,
                                   ‘trsvcid’: ‘4420’},
                                 {‘transport’: ‘RDMA’,
                                  ‘traddr’: ‘192.168.100.9’,
                                  ‘trsvcid’: ‘4420’}]
        :type listen_addresses: list of dicts
        :param hosts: Host nqn list. Example:
                      ['nqn.2016-06.io.spdk:init’,
                       ‘nqn.2016-07.io.spdk:init'].
        :type hosts: list of strings
        :param pci_address: Valid if mode == Direct.
                            Format:  'domain:device:function'
                            Example: '0000:00:01.0'.
        :type pci_address: string
        :param serial_number: Valid if mode == Virtual.
                              Format:  'sn'
                              Example: 'SPDK00000000000001'.
        :type serial_number: string
        :param namespaces: List of namespaces.
                           Example: 'Malloc0 Malloc1 Malloc2'
                           *** The devices must pre-exist ***.
        :type namespaces: list of strings
        :returns: None
        """

        return self.client.call(
            'construct_nvmf_subsystem', {
                'core': core,
                'mode': mode,
                'nqn': nqn,
                'listen_addresses': listen_addresses,
                'hosts': hosts,
                'pci_address': pci_address,
                'serial_number': serial_number,
                'namespaces': namespaces
            })

    def delete_nvmf_subsystem(self, nqn_name):
        """DDelete a nvmf subsystem.

        :param nqn_name: subsystem nqn to be deleted.
                         Example: nqn.2016-06.io.spdk:cnode1.
        :type nqn_name: string
        :returns: None
        """

        return self.client.call(
            'delete_nvmf_subsystem', {
                'nqn': nqn_name
            })

    def get_nvmf_subsystems(self, target_node_name):
        """Display nvmf subsystems.

        :returns: dict -- nvmf_subsystem object
        """

        return self.client.call('get_nvmf_subsystems', None)

    def kill(self, sig_name):
        """Send signal to instance.

        :param sig_name: signal will be sent to server.
        :type sig_name: string
        :returns: dict
        """

        return self.client.call('kill_instance', {'sig_name': sig_name})
