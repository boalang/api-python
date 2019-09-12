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
import xmlrpc.client
import traceback
from boaapi.util import parse_job
from boaapi.util import CookiesTransport

BOA_PROXY = "http://boa.cs.iastate.edu/boa/?q=boa/api"

class NotLoggedInException(Exception):
  pass

class BoaException(Exception):
    pass

class BoaClient(object):
    """ A client class for accessing boa's api 

    Attributes:
        server (xmlrpc.client.ServerProxy):
        trans (xmlrpc.client.Transport)
    """

    def __init__(self):
        """Create a new Boa API client, using the standard domain/path."""
        self.trans = CookiesTransport()
        self.__logged_in = False
        self.server = xmlrpc.client.ServerProxy(BOA_PROXY, transport=self.trans)

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
        except xmlrpc.client.Fault as e:
            raise BoaException(e).with_traceback(e.__traceback__)
            
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
            raise BoaException(e).with_traceback(e.__traceback__)

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
            raise BoaException(e).with_traceback(e.__traceback__)

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
            raise BoaException(e).with_traceback(e.__traceback__)

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
            raise BoaException(e).with_traceback(e.__traceback__)

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
            raise BoaException(e).with_traceback(e.__traceback__)

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
            raise BoaException(e).with_traceback(e.__traceback__)

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
            id = 0 if dataset is None else dataset.get_id()
            job = self.server.boa.submit(query, self.datasets()[id]['id'])
            return parse_job(self, job)
        except xmlrpc.client.Fault as e:
            raise BoaException(e).with_traceback(e.__traceback__)

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
            raise BoaException(e).with_traceback(e.__traceback__)

    def job_list(self, pub_only=False, offset=0, length=1000):
        """Returns a list of the most recent jobs, based on an offset and length.
        
        This includes public and private jobs.  Returned jobs are ordered from newest to oldest

        Args:
            pub_only (bool, optional): if true, only return public jobs otherwise return all jobs
            offset  (int, optional): the starting offset
            length (int, optional): the number of jobs (at most) to return

        Returns:
            list: a list of jobs where each element is a jobHandle
            
        Raises:
            BoaException: if theres an issue reading from the server
        """
        self.ensure_logged_in()
        try:
            list = self.server.boa.jobs(pub_only, offset, length)
            newDict = []
            if(len(list) > 0):
                for i in list:
                    newDict.append(parse_job(self, i))
            return newDict
        except xmlrpc.client.Fault as e:
            raise BoaException(e).with_traceback(e.__traceback__)

    def stop(self, job):
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
            raise BoaException(e).with_traceback(e.__traceback__)

    def resubmit(self, job):
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
            raise BoaException(e).with_traceback(e.__traceback__)

    def delete(self, job):
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
            raise BoaException(e).with_traceback(e.__traceback__)

    def set_public(self, job, is_public):
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
            raise BoaException(e).with_traceback(e.__traceback__)

    def public_status(self, job):
        """Get the jobs public/private status.
        
        Args: 
            job (JobHandle)
            
        Raises:
            BoaException: if theres an issue reading from the server
        """
        self.ensure_logged_in()
        try:
            result = self.server.job.public(job.id)
            if result is 1:
                return True
            else:
                return False
        except xmlrpc.client.Fault as e:
            raise BoaException(e).with_traceback(e.__traceback__)

    def get_url(self, job):
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
            raise BoaException(e).with_traceback(e.__traceback__)

    def public_url(self, job):
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
            raise BoaException(e).with_traceback(e.__traceback__)

    def get_compiler_errors(self, job):
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
            raise BoaException(e).with_traceback(e.__traceback__)

    def source(self, job):
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
            raise BoaException(e).with_traceback(e.__traceback__)

    def output(self, job):
        """Return the output for this job, if it finished successfully and has an output.
        
        Raises:
            BoaException: if theres an issue reading from the server
        """
        self.ensure_logged_in()
        try:
            if job.exec_status != "Finished":
                return "Job is currently running"
            return self.server.job.output(job.id)
        except xmlrpc.client.Fault as e:
            raise BoaException(e).with_traceback(e.__traceback__)
