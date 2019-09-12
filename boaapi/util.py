#
# Copyright 2019, Hridesh Rajan, Kamsi Ibeziako, Robert Dyer,
#                 Bowling Green State University
#                 and Iowa State University of Science and Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import xmlrpc
from boaapi.job_handle import JobHandle

class CookiesTransport(xmlrpc.client.Transport):
    """A Transport subclass that retains cookies over its lifetime."""

    def __init__(self):
        super().__init__()
        self._cookies = []
        self._csrf = []

    def add_csrf(self, token):
        self._csrf.append(token)

    def send_headers(self, connection, headers):
        if self._cookies:
            connection.putheader("Cookie", "; ".join(self._cookies))
            connection.putheader("X-CSRF-Token", "; ".join(self._csrf))
        super().send_headers(connection, headers)

    def parse_response(self, response):
        session_message = response.msg.get_all("Set-Cookie")
        if session_message is not None:
            for header in response.msg.get_all("Set-Cookie"):
                cookie = header.split(";", 1)[0]
                self._cookies.append(cookie)
        return super().parse_response(response)

def parse_job(client, job):
    return JobHandle(client, job['id'], job['submitted'], job['input'], job['compiler_status'], job['hadoop_status'])
