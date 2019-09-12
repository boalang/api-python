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
class JobHandle:
    """A class for handling jobs sent to the framework

    Attributes:
        client (BoaClient): the xmlrpc client
        id (int): the jobs id
        date (str): the date and time the job was submitted
        dataset (dict): the dataset used to executed the job
        exec_status (str): the execution status for the job
        compiler_status (str): the compiler status for the job
    """

    def __init__(self, client, id, date, dataset, compiler_status, exec_status):
        self.client = client
        self.id = id
        self.date = date
        self.dataset = dataset
        self.compiler_status = compiler_status
        self.exec_status = exec_status

    def __str__(self):
        """string output for a job"""
        return str('id: ' + str(self.id) + ', date:' + str(self.date) +
        ', dataset:' + str(self.dataset) + ', compiler_status: (' + str(self.compiler_status) + ')'
        +', execution_status: (' + str(self.exec_status) + ')')

    def stop(self):
        """Stops the job if it is running."""
        return self.client.stop(self)

    def resubmit(self):
        """Resubmits this job."""
        return self.client.resubmit(self)

    def delete(self):
        """Deletes this job from the framework."""
        return self.client.delete(self)

    def get_url(self):
        """Retrieves the jobs URL."""
        return self.client.get_url(self)

    def set_public(self, status):
        """Modifies the public/private status of this job.

        Args:
            status (bool): 'True' to make it public, False to make it private
        """
        return self.client.set_public(self, status)

    def public_status(self):
        """Get the jobs public/private status."""
        return self.client.public_status(self)

    def public_url(self):
        """Get the jobs public page URL."""
        return self.client.public_url(self)

    def source(self):
        """Return the source query for this job."""
        return self.client.source(self)

    def get_compiler_errors(self):
        """Return any errors from trying to compile the job."""
        return self.client.get_compiler_errors(self)

    def output(self):
        """Return the output for this job, if it finished successfully and has output."""
        return self.client.output(self)

    def output_size(self):
        """Return the output size for this job, if it finished successfully and has output."""
        return self.client.output_size(self)

    def refresh(self):
        """Refreshes the cached data for this job."""
        job = self.client.get_job(self.id)
        self.compiler_status = job.compiler_status
        self.exec_status = job.exec_status
        self.date = job.date
