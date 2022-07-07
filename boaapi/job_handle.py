#
# Copyright 2019-2022, Hridesh Rajan, Kamsi Ibeziako, Robert Dyer,
#                 Bowling Green State University
#                 Iowa State University of Science and Technology
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
from boaapi.status import CompilerStatus, ExecutionStatus

class JobHandle:
    """A class for handling jobs sent to the framework.
    This class is not intended to be instantiated directly.
    Please use the BoaClient class to obtain instances of JobHandle.

    Attributes:
        client (BoaClient): the xmlrpc client
        id (int): the jobs id
        date (str): the date and time the job was submitted
        dataset (dict): the dataset used to executed the job
        exec_status (int): the execution status for the job
        compiler_status (int): the compiler status for the job
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
        self.client._stop(self)

    def resubmit(self):
        """Resubmits this job."""
        return self.client._resubmit(self)

    def delete(self):
        """Deletes this job from the framework."""
        self.client._delete(self)

    def get_url(self):
        """Retrieves the jobs URL."""
        return self.client._get_url(self)

    def set_public(self, status):
        """Modifies the public/private status of this job.

        Args:
            status (bool): 'True' to make it public, False to make it private
        """
        self.client._set_public(self, status)

    def get_public(self):
        """Get the jobs public/private status."""
        return self.client._public_status(self)

    def get_public_url(self):
        """Get the jobs public page URL."""
        return self.client._public_url(self)

    def source(self):
        """Return the source query for this job."""
        return self.client._source(self)

    def get_compiler_errors(self):
        """Return any errors from trying to compile the job."""
        return self.client._get_compiler_errors(self)

    def output(self):
        """Return the output for this job, if it finished successfully and has output."""
        return self.client._output(self)

    def output_size(self):
        """Return the output size for this job, if it finished successfully and has output."""
        return self.client._output_size(self)

    def output_hash(self):
        """Return a number of bytes and hash of the output for this job, if it finished successfully and has output."""
        return self.client._output_hash(self)

    def wait(self):
        """Waits for a job to finish.

        Returns:
            boolean indicating if the job had no error
        """
        from time import sleep
        while self.is_running():
            sleep(2)
            self.refresh()
        return not (self.compiler_status is CompilerStatus.ERROR or self.exec_status is ExecutionStatus.ERROR)

    def refresh(self):
        """Refreshes the cached data for this job."""
        job = self.client.get_job(self.id)
        self.compiler_status = job.compiler_status
        self.exec_status = job.exec_status
        self.date = job.date

    def is_running(self):
        return self.compiler_status is CompilerStatus.RUNNING or self.exec_status is ExecutionStatus.RUNNING or self.compiler_status is CompilerStatus.WAITING or (self.exec_status is ExecutionStatus.WAITING and self.compiler_status is CompilerStatus.FINISHED)
