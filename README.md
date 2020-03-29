# About Boa Python Client API

The Boa Python Client API provides programmatic access to the Boa language and infrastructure from Python.

## About Boa

For more information about Boa, please see the main website: http://boa.cs.iastate.edu/

## Example Use

````python
import time

from boaapi.boa_client import BoaClient

client = BoaClient()
client.login("boa username", "boa password")
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

if job.compiler_status == 'Error':
    print('job ' + str(job.id) + ' had compile error')
elif job.exec_status == 'Error':
    print('job ' + str(job.id) + ' had exec error')
else:
    try:
        output = job.output().decode('utf-8')
        print('output:')
        print(output)
    except:
        pass

client.close()
print('client closed')
````
