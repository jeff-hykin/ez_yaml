# Install

`pip install python-include`

# Use

```
import include

# import [name] from-anywhere (doesnt pollute global namespace)
hello = include.file("./path/to/file/with/hello/func/code.py", {"__file__":__file__}).hello
hello()

# import [*everything*] from-anywhere (does pollute global namespace)
include.file("./path/to/file/with/hello/func/code.py", globals())
hello() # function that was defined inside that^ "code.py"
```
