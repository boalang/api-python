import xmlrpc
from job_handle import JobHandle

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
