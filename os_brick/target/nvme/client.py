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

import json
import requests
import socket

from os_brick import exception


class NVMeRPCClient(object):

    def __init__(self, ip_address='127.0.0.1', port=4420, instance_id=0):
        self.url = "http://{ip_address}:{port}/jsonrpc".format(
            ip_address=ip_address, port=port + instance_id)

        self.server_ip = ip_address
        self.port = port
        self.instance_id = instance_id
        self.headers = {'content-type': 'application/json'}
        self.payload = {'jsonrpc': '2.0', 'id': 1}

    def call(self, method, params):
        self.payload['method'] = method
        if params:
            self.payload['params'] = params

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.server_ip, self.port + self.instance_id))
        req = {}
        req['jsonrpc'] = '2.0'
        req['method'] = method
        req['id'] = 1
        if params:
            req['params'] = params
        reqstr = json.dumps(req)
        s.sendall(reqstr)
        buf = ''
        closed = False
        response = {}

        while not closed:
            newdata = s.recv(4096)
            if (newdata == b''):
                closed = True
            buf += newdata
            try:
                response = json.loads(buf)
            except ValueError:
                continue  # incomplete response; keep buffering
            break
        s.close()

#        response = requests.post(
#            self.url,
#            data=json.dumps(self.payload)).json()
#            headers=self.headers).json()
#
        if 'error' in response:
            raise exception.NVMeRPCException(
                message=response['error']['message'])

        return response['result']
