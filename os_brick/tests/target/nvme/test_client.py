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
import mock
import requests

from os_brick import exception
from os_brick.target.nvme import client
from os_brick.tests import base


class NVMeRPCClientTestCase(base.TestCase):

    def setUp(self):
        super(NVMeRPCClientTestCase, self).setUp()
        self.client = client.NVMeRPCClient()

    def test_call(self):
        expected_url = "http://{ip_address}:{port}/jsonrpc".format(
            ip_address='127.0.0.1', port=5260)
        params = {'param1': 'value_1'}
        method_name = 'some_method'

        with mock.patch.object(requests, 'post') as post_mock:
            post_mock.return_value = MockHTTPSResponse('some_content')
            response = self.client.call(method_name, params)
            post_mock.assert_called_once_with(
                expected_url,
                data=json.dumps({'jsonrpc': '2.0', 'id': 1,
                                 'method': method_name, 'params': params}),
                headers={'content-type': 'application/json'}
            )
            self.assertEqual({'data': 'some_content'}, response)

    def test_call_with_error(self):
        with mock.patch.object(
                requests, 'post', return_value=MockHTTPSResponse(
                    None, error_msg='Some error')):
            with self.assertRaisesRegexp(exception.NVMeRPCException,
                                         'Some error'):
                self.client.call('some_method', None)


class MockHTTPSResponse(object):
    def __init__(self, content, error_msg=None):
        self._content = content
        self._error_msg = error_msg

    def json(self, **kwargs):
        result = {'data': self._content}
        if self._error_msg:
            result.update({'error': {'message': self._error_msg}})
        return result
