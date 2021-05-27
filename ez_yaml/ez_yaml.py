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