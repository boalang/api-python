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
import xml
import xmlrpc.client
from boaapi.util import BoaException, CookiesTransport, parse_job, fetch_url
from boaapi.status import CompilerStatus, ExecutionStatus

BOA_API_ENDPOINT = "https://boa.cs.iastate.edu/boa/?q=boa/api"
BOAC_API_ENDPOINT = "https://boa.cs.iastate.edu/boac/?q=boa/api"

class NotLoggedInException(Exception):
    pass

class BoaClient(object):
    """ A client class for accessing boa's api

    Attributes:
        server (xmlrpc.client.ServerProxy):
        trans (xmlrpc.client.Transport)
    """

    def __init__(self, endpoint = BOA_API_ENDPOINT):
        """Create a new Boa API client, using the standard domain/path.

        Args:
            endpoint (str): The API endpoint URL to use, defaults to BOA_API_ENDPOINT
        """
        self.trans = CookiesTransport()
        self.__logged_in = False
        self.server = xmlrpc.client.ServerProxy(endpoint, transport=self.trans)

    def login(self, username, password):
        """log into the boa framework using the remote api

        Args:
            username (str): username for boa account
            password (str): password for boa account
        """
        try:
            self.__logged_in = True
            response = self.server.user.login(username, password)
            self.trans.add_csrf(response["token"])
            return response
        except xml.parsers.expat.ExpatError as e:
            raise BoaException("XMLRPC problem - most likely you have an invalid ENDPOINT set. Try using: BoaClient(endpoint=BOA_API_ENDPOINT)") from e
        except xmlrpc.client.Fault as e:
            raise BoaException() from e

    def close(self):
        """Log out of the boa framework using the remote api

        Raises:
            BoaException: if theres an issue reading from the server
        """
        self.ensure_logged_in()
        try:
            self.server.user.logout()
            self.__logged_in = False
        except xmlrpc.client.Fault as e:
            raise BoaException() from e

    def ensure_logged_in(self):
        """Checks if a user is currently logged in through the remote api

        Returns:
            bool: True if user is logged in, false if otherwise

        Raises:
            NotLoggedInException: if user is not currently logged in
        """
        if not self.__logged_in:
            raise NotLoggedInException("User not currently logged in")

    def datasets(self):
        """ Retrieves datasetsets currently provided by boa

        Returns:
            list: a list of boa datasets

        Raises:
            BoaException: if theres an issue reading from the server
        """
        self.ensure_logged_in()
        try:
            return self.server.boa.datasets()
        except xmlrpc.client.Fault as e:
            raise BoaException() from e

    def dataset_names(self):
        """Retrieves a list of names of all datasets provided by boa

        Returns:
            list: the dataset names

        Raises:
            BoaException: if theres an issue reading from the server
        """
        self.ensure_logged_in()
        try:
            dataset_names = []
            datasets = self.datasets()
            for x in datasets:
                dataset_names.append(x['name'])
            return dataset_names
        except xmlrpc.client.Fault as e:
            raise BoaException() from e

    def get_dataset(self, name):
        """Retrieves a dataset given a name.

        Args:
            name (str): The name of the input dataset to return.

        Returns:
            dict: a dictionary with the keys id and name

        Raises:
            BoaException: if theres an issue reading from the server
        """
        self.ensure_logged_in()
        try:
            for x in self.datasets():
                if x['name'] == name:
                    return x
            return None
        except xmlrpc.client.Fault as e:
            raise BoaException() from e

    def last_job(self):
        """Retrieves the most recently submitted job

        Returns:
            JobHandle: the last submitted job

        Raises:
            BoaException: if theres an issue reading from the server
        """
        self.ensure_logged_in()
        try:
            jobs = self.job_list(False, 0, 1)
            return jobs[0]
        except xmlrpc.client.Fault as e:
            raise BoaException() from e

    def job_count(self, pub_only=False):
        """Retrieves the number of jobs submitted by a user

        Args:
            pub_only (bool, optional): if true, return only public jobs
                otherwise return all jobs

        Returns:
            int: the number of jobs submitted by a user

        Raises:
            BoaException: if theres an issue reading from the server
        """
        self.ensure_logged_in()
        try:
            return self.server.boa.count(pub_only)
        except xmlrpc.client.Fault as e:
            raise BoaException() from e

    def query(self, query, dataset=None):
        """Submits a new query to Boa to query the specified and returns a handle to the new job.

        Args:
            query (str): a boa query represented as a string.
            dataset (str, optional): the name of the input dataset.

        Returns:
            (JobHandle) a job

        Raises:
            BoaException: if theres an issue reading from the server
        """
        self.ensure_logged_in()
        try:
            if dataset is None:
                dataset = self.datasets()[0]
            return parse_job(self, self.server.boa.submit(query, dataset.get('id')))
        except xmlrpc.client.Fault as e:
            raise BoaException() from e

    def get_job(self, id):
        """Retrieves a job given an id.

        Args:
            id (int): the id of the job you want to retrieve

        Returns:
            JobHandle: the desired job.

        Raises:
            BoaException: if theres an issue reading from the server
        """
        self.ensure_logged_in()
        try:
            return parse_job(self, self.server.boa.job(id))
        except xmlrpc.client.Fault as e:
            raise BoaException() from e

    def job_list(self, pub_only=False, offset=0, length=1000):
        """Returns a list of the most recent jobs, based on an offset and length.

        This includes public and private jobs.  Returned jobs are ordered from newest to oldest

        Args:
            pub_only (bool, optional): if true, only return public jobs otherwise return all jobs
            offset  (int, optional): the starting offset
            length (int, optional): the number of jobs (at most) to return

        Returns:
            list: a list of jobs where each element is a JobHandle

        Raises:
            BoaException: if theres an issue reading from the server
        """
        self.ensure_logged_in()
        try:
            list = self.server.boa.range(pub_only, offset, length)
            jobs = []
            if (len(list) > 0):
                for i in list:
                    jobs.append(parse_job(self, i))
            return jobs
        except xmlrpc.client.Fault as e:
            raise BoaException() from e

    ####################################################################
    # the methods below are not meant to be called by clients directly #
    # but rather through a handle                                      #
    ####################################################################

    def _stop(self, job):
        """Stops the execution of a job

        Args:
            job (JobHandle): the job whose execution you want to stop

        Raises:
            BoaException: if theres an issue reading from the server
        """
        self.ensure_logged_in()
        try:
            self.server.job.stop(job.id)
        except xmlrpc.client.Fault as e:
            raise BoaException() from e

    def _resubmit(self, job):
        """Resubmits a job to the framework

        Args:
            job (JobHandle): The job you want to resubmit

        Raises:
            BoaException: if theres an issue reading from the server
        """
        self.ensure_logged_in()
        try:
            self.server.job.resubmit(job.id)
        except xmlrpc.client.Fault as e:
            raise BoaException() from e

    def _delete(self, job):
        """Deletes this job from the framework.

        Args:
            job (JobHandle): the job you want to delete

        Raises:
            BoaException: if theres an issue reading from the server
        """
        self.ensure_logged_in()
        try:
            self.server.job.delete(job.id)
        except xmlrpc.client.Fault as e:
            raise BoaException() from e

    def _set_public(self, job, is_public):
        """Modifies the public/private status of this job.

        Args:
            is_public (bool): 'True' to make it public, False to make it private
            job (JobHandle)

        Raises:
            BoaException: if theres an issue reading from the server
        """
        self.ensure_logged_in()
        try:
            if is_public is True:
                self.server.job.setpublic(job.id, 1)
            else:
                self.server.job.setpublic(job.id, 0)
        except xmlrpc.client.Fault as e:
            raise BoaException() from e

    def _public_status(self, job):
        """Get the jobs public/private status.

        Args:
            job (JobHandle)

        Raises:
            BoaException: if theres an issue reading from the server
        """
        self.ensure_logged_in()
        try:
            result = self.server.job.public(job.id)
            if result == 1:
                return True
            else:
                return False
        except xmlrpc.client.Fault as e:
            raise BoaException() from e

    def _get_url(self, job):
        """Retrieves the jobs URL.

        Args:
            job (JobHandle)

        Raises:
            BoaException: if theres an issue reading from the server
        """
        self.ensure_logged_in()
        try:
            return self.server.job.url(job.id)
        except xmlrpc.client.Fault as e:
            raise BoaException() from e

    def _public_url(self, job):
        """Get the jobs public page URL.

        Args:
            job (JobHandle)

        Raises:
            BoaException: if theres an issue reading from the server
        """
        self.ensure_logged_in()
        try:
            return self.server.job.publicurl(job.id)
        except xmlrpc.client.Fault as e:
            raise BoaException() from e

    def _get_compiler_errors(self, job):
        """Return any errors from trying to compile the job.

        Args:
            job (JobHandle)

        Raises:
            BoaException: if theres an issue reading from the server
        """
        self.ensure_logged_in()
        try:
            return self.server.job.compilerErrors(job.id)
        except xmlrpc.client.Fault as e:
            raise BoaException() from e

    def _source(self, job):
        """Return the source query for this job.

        Args:
            job (JobHandle)

        Raises:
            BoaException: if theres an issue reading from the server
        """
        self.ensure_logged_in()
        try:
            return self.server.job.source(job.id)
        except xmlrpc.client.Fault as e:
            raise BoaException() from e

    def _output(self, job):
        """Return the output for this job, if it finished successfully and has an output.

        Raises:
            BoaException: if theres an issue reading from the server
        """
        self.ensure_logged_in()
        try:
            if job.exec_status != ExecutionStatus.FINISHED:
                raise BoaException("Job is currently running")
            return fetch_url(self.server.job.output(job.id)).decode('utf-8')
        except xmlrpc.client.Fault as e:
            raise BoaException() from e

    def _output_size(self, job):
        """Return the output size for this job, if it finished successfully and has an output.

        Raises:
            BoaException: if theres an issue reading from the server
        """
        self.ensure_logged_in()
        try:
            if job.exec_status != ExecutionStatus.FINISHED:
                raise BoaException("Job is currently running")
            return self.server.job.outputsize(job.id)
        except xmlrpc.client.Fault as e:
            raise BoaException() from e

    def _output_hash(self, job):
        """Return a number of bytes and hash of the output for this job, if it finished successfully and has output.

        Raises:
            BoaException: if theres an issue reading from the server
        """
        self.ensure_logged_in()
        try:
            if job.exec_status != ExecutionStatus.FINISHED:
                raise BoaException("Job is currently running")
            res = self.server.job.outputhash(job.id)
            return (int(res[0]), str(res[1]))
        except xmlrpc.client.Fault as e:
            raise BoaException() from e
