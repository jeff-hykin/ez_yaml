from .__dependencies__ import ruamel 
from .__dependencies__.ruamel import yaml
from io import StringIO
from pathlib import Path
import os

def _get_default_settings():
    return dict(
        safe=False,
        width=None,
        allow_duplicate_keys=True,
        explicit_start=False,
        explicit_end=False,
        explict_null=True,
        indent_mapping=3,
        indent_sequence=2,
        offset=0,
    )

settings = _get_default_settings()
global_settings = settings # alias (prefered name, but dont want to break backwards compat)

# setup loader (basically options)
def get_yaml(settings={}):
    settings_with_defaults = _get_default_settings()
    settings_with_defaults.update(settings or {})
    settings = settings_with_defaults
    if settings["safe"]:
        yaml = ruamel.yaml.YAML(type="safe")
    else:
        yaml = ruamel.yaml.YAML()
    
    yaml.indent(mapping=settings["indent_mapping"], sequence=settings["indent_sequence"], offset=settings["offset"])
    yaml.allow_duplicate_keys = settings["allow_duplicate_keys"]
    yaml.width = settings["width"]
    yaml.explicit_start = settings["explicit_start"]
    yaml.explicit_end = settings["explicit_end"]
    
    if settings["explict_null"]:
        yaml.representer.add_representer(
            type(None),
            lambda self, data: self.represent_scalar(u'tag:yaml.org,2002:null', u'null')
        )
    return yaml

yaml = get_yaml()

def to_string(obj, options=None, settings=None):
    if options == None: options = {}
    if settings == None: settings = {}
    yaml = get_yaml({**global_settings, **settings, })
    string_stream = StringIO()
    yaml.dump(obj, string_stream, **options)
    output_str = string_stream.getvalue()
    string_stream.close()
    return output_str

def to_object(string=None, file_path=None, options=None, load_nested_yaml=False, settings=None):
    if options == None: options = {}
    if settings == None: settings = {}
    yaml = get_yaml({**global_settings, **settings, })
    if file_path is not None:
        as_path_object = Path(file_path)
        output = yaml.load(as_path_object, **options)
        if load_nested_yaml:
            output = eval_load_yaml_file_tag(output, original_file_path=file_path) 
        return output
    else:
        output = yaml.load(string, **options)
        if load_nested_yaml:
            output = eval_load_yaml_file_tag(output, original_file_path=":<inline-string>:") 
        return output

def to_file(obj, file_path, options=None, settings=None):
    if options == None: options = {}
    if settings == None: settings = {}
    yaml = get_yaml({**global_settings, **settings, })
    as_path_object = Path(file_path)
    with as_path_object.open('w') as output_file:
        return yaml.dump(obj, output_file, **options)

def eval_load_yaml_file_tag(yaml_obj, key_list=[], original_file_path=""):
    """
    # file1.yaml
    thing: !load_yaml_file ./file2.yaml
    
    # file2.yaml
    value1: 1
    value2: 2
    """
    if isinstance(yaml_obj, ruamel.yaml.comments.TaggedScalar):
        tag = yaml_obj.tag.value
        # if has the !load_yaml_file
        if tag == "!load_yaml_file":
            load_file_path = yaml_obj.value
            # make the path relative to the yaml file instead of cwd
            if not os.path.isabs(load_file_path):
                load_file_path = os.path.join(os.path.dirname(original_file_path), load_file_path)
            try:
                data = to_object(file_path=load_file_path)
                return data
            except Exception as error:
                if not os.path.isfile(load_file_path):
                    raise Exception(f"""
                    
                        ---------------------------------------------------------------------------------
                        When loading the yaml file: {original_file_path}
                        following these keys {key_list}
                        there is a value of: {tag} "{load_file_path}"
                        
                        So I tried to load "{load_file_path}" but it doesn't seem to exist
                        
                        LIKELY SOLUTION:
                            Create a yaml file at "{load_file_path}"
                        
                        ALTERNATIVE SOLUTIONS:
                            - Fix an error with the file path
                            - Comment out the line with !load_yaml_file
                            - Remove just the "!load_yaml_file" from the line
                        ---------------------------------------------------------------------------------
                    """.replace("\n                    ", "\n"))
                else:
                    raise Exception(f"""
                    
                        ---------------------------------------------------------------------------------
                        When loading the yaml file: {original_file_path}
                        following these keys {key_list}
                        there is a value of: {tag} "{load_file_path}"
                        
                        So I tried to load "{load_file_path}" but it threw an error:
                        
                        __error__
                        {error}
                        __error__
                        
                        LIKELY SOLUTION:
                            The yaml file at: "{load_file_path}"
                            is corrupt/invalid so fix the syntax errors with it
                        
                        ALTERNATIVE SOLUTIONS:
                            - Comment out the line with !load_yaml_file
                            - Have make the file path to a different file
                            - Remove just the "!load_yaml_file" from the line
                        ---------------------------------------------------------------------------------
                    """.replace("\n                    ", "\n"))
        
    if isinstance(yaml_obj, dict):
        return {
            key : eval_load_yaml_file_tag(value, key_list=key_list+[key], original_file_path=original_file_path)
            
            for key, value in yaml_obj.items() 
        }
    elif isinstance(yaml_obj, list):
        return [
            eval_load_yaml_file_tag(value, key_list=key_list+[key], original_file_path=original_file_path)
            
            for key, value in enumerate(yaml_obj)
        ]
    else:
        return yaml_obj

def merge_files_to_object(*files, options=None, settings=None):
    if options == None: options = {}
    if settings == None: settings = {}
    yaml = get_yaml({**global_settings, **settings, })
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