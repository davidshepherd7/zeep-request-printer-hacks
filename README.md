A hacked version of zeep to print requests.

Usage:

* Clone the repo
* Run ipython like `export PYTHONPATH="/path/to/this/dir/src" ipython3`

Then inside ipython you can do things like:
```
import zeep

c = zeep.client("path/to/wsdl/file")

c.service. # Hit tab to see possible commands

c.service.SomeCommand? # Shows the arguments needed

c.service.SomeCommand({"foo": "an argument", "bar": 123})
# Prints the details of the HTTP request that would be made then raises an exception
```
