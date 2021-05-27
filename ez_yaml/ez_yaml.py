import ruamel.yaml
from io import StringIO
from pathlib import Path

# setup loader (basically options)
yaml = ruamel.yaml.YAML()
yaml.version = (1, 2)
yaml.indent(mapping=3, sequence=2, offset=0)
yaml.allow_duplicate_keys = True
yaml.explicit_start = False
# show null
yaml.representer.add_representer(
    type(None),
    lambda self, data: self.represent_scalar(u'tag:yaml.org,2002:null', u'null')
)

def to_string(obj, options=None):
    if options == None: options = {}
    string_stream = StringIO()
    yaml.dump(obj, string_stream, **options)
    output_str = string_stream.getvalue()
    string_stream.close()
    return output_str

def to_object(string=None, file_path=None, options=None):
    if options == None: options = {}
    if file_path is not None:
        as_path_object = Path(file_path)
        return yaml.load(as_path_object, **options)
    else:
        return yaml.load(string, **options)

def to_file(obj, file_path, options=None):
    if options == None: options = {}
    as_path_object = Path(file_path)
    with as_path_object.open('w') as output_file:
        return yaml.dump(obj, output_file, **options)

def merge_files_to_object(*files, options=None):
    if options == None: options = {}
    # yup ... this is how to check
    # https://stackoverflow.com/questions/1952464/in-python-how-do-i-determine-if-an-object-is-iterable
    def is_iterable(thing):
        try:
            iter(thing)
        except TypeError:
            return False
        else:
            return True
    import collections.abc
    def merge(old_value, new_value):
        # if not dict, see if it is iterable
        if not isinstance(new_value, collections.abc.Mapping):
            if is_iterable(new_value):
                new_value = { index: value for index, value in enumerate(new_value) }
        
        # if still not a dict, then just return the current value
        if not isinstance(new_value, collections.abc.Mapping):
            return new_value
        # otherwise get recursive
        else:
            # if not dict, see if it is iterable
            if not isinstance(old_value, collections.abc.Mapping):
                if is_iterable(old_value):
                    old_value = { index: value for index, value in enumerate(old_value) }
            # if still not a dict
            if not isinstance(old_value, collections.abc.Mapping):
                # force it to be one
                old_value = {}
            
            # override each key recursively
            for key, updated_value in new_value.items():
                old_value[key] = merge(old_value.get(key, {}), updated_value)
            
            return old_value
        
    running_object = {}
    for file in files:
        running_object = merge(running_object, yaml.load(Path(file), **options))

    return running_object


def _convert_to_yaml(representer, yaml_tag, value):
    from datetime import date, datetime
    print('type(value) = ', type(value))
    # detect value type
    if value is None:
        print('none')
        # use string otherwise it puts a blank space/area
        # this is still equivlent to null because there's no quotes
        output = representer.represent_str("null")
        output.tag = yaml_tag
        return output
    elif type(value) is bool:
        print('bool')
        output = representer.represent_bool(value)
        output.tag = yaml_tag
        return output
    elif type(value) is int:
        print('int')
        output = representer.represent_int(value)
        output.tag = yaml_tag
        return output
    elif type(value) is float:
        print('float')
        output = representer.represent_float(value)
        output.tag = yaml_tag
        return output
    elif type(value) is str:
        print('str')
        output = representer.represent_str(value)
        # use either block or quoted string styles
        output.style = "|" if "\n" in value else  "'"
        output.tag = yaml_tag
        return output
    elif isinstance(value, date):
        print('date')
        output = representer.represent_date( value)
        output.tag = yaml_tag
        return output
    elif isinstance(value, datetime):
        print('datetime')
        output = representer.represent_datetime(value)
        output.tag = yaml_tag
        return output
    elif isinstance(value, dict):
        print('dict')
        return representer.represent_mapping(yaml_tag, value)
    elif isinstance(value,list) or isinstance(value,tuple):
        print('list')
        return representer.represent_sequence(yaml_tag, value)
    else:
        raise Exception('Error: not sure how to convert '+str(type(value))+' to a yaml node')

class CustomObject:
    yaml_tag = '!argument'
    def __init__(self, value):
        self.value = value

    @classmethod
    def to_yaml(cls, representer, self):
        return _convert_to_yaml(representer, cls.yaml_tag, self.value)

    @classmethod
    def from_yaml(cls, constructor, node):
        from ruamel.yaml import YAML
        from ruamel.yaml.nodes import SequenceNode, MappingNode
        from ruamel.yaml.comments import CommentedMap
        # primitives
        if type(node.value) == str:
            print('node = ', node)
            # definitely a string
            if node.style is not None:
                return cls(node.value)
            else:
                # parse as a normal yaml value
                value = YAML().load(node.value)
                return cls(value)
        # lists
        elif type(node) == SequenceNode:
            list_values = constructor.construct_sequence(node, deep=True)
            return cls(list_values)
        # mappings
        elif type(node) == MappingNode:
            data = CommentedMap()
            constructor.construct_mapping(node, data, deep=True)
            return cls(data)

ez_yaml.yaml.register_class(CustomObject)

# TODO: make a class decorator for this
# TODO: make a functional decorator for this yaml.add_tag("!argument", lambda old_value: new_value)
# TODO: make a functional decorator for this yaml.add_class(AClass, lambda object: plain_python_obj)

my_object = ez_yaml.to_object("""
val1:
    value2: !argument "2001-12-14"
""")
print('my_object = ', my_object)
print('ez_yaml.to_string(my_object) = ', ez_yaml.to_string(my_object))
