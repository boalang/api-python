# About Boa Python Client API

The Boa Python Client API provides programmatic access to the Boa language and infrastructure from Python.

## About Boa

For more information about Boa, please see the main website: https://boa.cs.iastate.edu/

## Creating a client

The main entry point for the API is a `BoaClient` object.  You use this to log in, submit queries, find datasets, log out, etc.  To instantiate this object, you must provide the API endpoint's URL.  The API has several constants for common endpoints:

- `BOA_API_ENDPOINT` - for the Boa MSR endpoint
- `BOAC_API_ENDPOINT` - for the Boa CORD-19 endpoint

For example if you want a client for the CORD-19 endpoint, you do the following:

`client = BoaClient(endpoint=BOAC_API_ENDPOINT)`

If you don't specify an endpoint, it will default to the MSR endpoint.

## Example Use (using MSR endpoint)

````python
import getpass
import time

from boaapi.boa_client import BoaClient, BOA_API_ENDPOINT
from boaapi.status import CompilerStatus, ExecutionStatus

client = BoaClient(endpoint=BOA_API_ENDPOINT)
user = input("Username [%s]: " % getpass.getuser())
if not user:
    user = getpass.getuser()
client.login(user, getpass.getpass())
print('successfully logged in to Boa API')

query = """# Counting the 10 most used programming languages
p: Project = input;
counts: output top(10) of string weight int;

foreach (i: int; def(p.programming_languages[i]))
    counts << p.programming_languages[i] weight 1;"""

# query using a specific dataset
job = client.query(query, client.get_dataset('2019 October/GitHub'))
print('query submitted')

while job.is_running():
    job.refresh()
    print('job ' + str(job.id) + ' still running, waiting 10s...')
    time.sleep(10)

if job.compiler_status is CompilerStatus.ERROR:
    print('job ' + str(job.id) + ' had compile error')
elif job.exec_status is ExecutionStatus.ERROR:
    print('job ' + str(job.id) + ' had exec error')
else:
    try:
        print('output:')
        print(job.output())
    except:
        pass

client.close()
print('client closed')
````
