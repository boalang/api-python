#
# Copyright 2021, Robert Dyer,
#                 and University of Nebraska Board of Regents
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
import xmlrpc.client
import http.client
from boaapi.boa_client import BoaClient
from boaapi.job_handle import JobHandle
from typing import List, Tuple

class CookiesTransport(xmlrpc.client.Transport):
    def __init__(self) -> None: ...
    def add_csrf(self, token: str) -> None: ...
    def send_headers(self, connection: http.client.HTTPConnection, headers: List[Tuple[str, str]]) -> None: ...
    def parse_response(self, response): ...

def parse_job(client: BoaClient, job) -> JobHandle: ...
def parse_compiler_status(status: str) -> str: ...
def parse_execution_status(status: str) -> int: ...
def fetch_url(url: str) -> str: ...
