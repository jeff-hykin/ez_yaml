# Install

`pip install ez_yaml`

# Use

```python
import ez_yaml

# to_string(obj, options={})
ez_yaml.to_string({"thing": 1, "abc": [ 1,2,3 ]})

# to_object(file_path, options={})
# to_object(string   , options={})
ez_yaml.to_object(string='''

thing: 1
abc:
    - 1
    - 2
    - 3

''')

# to_file(obj, file_path, options={})
ez_yaml.to_file(
    {"thing": 1, "abc": [ 1,2,3 ]},
    file_path="./my_file.yaml",
)