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
