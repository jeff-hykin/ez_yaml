# Install

`pip install python-include`

# Use

```
import include
include.file("./relative/path/to/code.py", globals())

hello() # function that was normally defined inside the "code.py"
```