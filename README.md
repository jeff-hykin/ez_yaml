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

```

# Custom Yaml Tags Example

```py
from ez_yaml import yaml

@yaml.register_class
class YourCustomClass:
    yaml_tag = "!python/YourCustomClass"
    
    def __init__(self, something):
        self.something = something
    
    @classmethod
    def from_yaml(cls, constructor, node):
        # will print true
        print(node.value.startswith("blah blah YourCustomClass(something:"))
        # node.value is the python-value
        return YourCustomClass(something=node.value[len("blah blah YourCustomClass(something:")-1:-1])
    
    @classmethod
    def to_yaml(cls, representer, object_of_this_class):
        representation = f"blah blah YourCustomClass(something:{object_of_this_class.something})"
        # ^ needs to be a string (or some other yaml-primitive)
        return representer.represent_scalar(
            tag=cls.yaml_tag,
            value=representation,
            style=None,
            anchor=None
        )


data = [
    YourCustomClass(['blah blah blah']),
    YourCustomClass({"thing": "lorem ipsum"}),
]

# will get generated with a tag
output = ez_yaml.to_string(data)
# will detect tag and convert it back to a YourCustomClass
yaml.load(output)
```