import sys
import os
import inspect
import textwrap
import importlib
from os.path import isabs, isfile, isdir, join, dirname, basename, exists, splitext, relpath, abspath, normpath

ModuleClass = type(sys)
dont_override = ( '__name__', '__doc__', '__package__', '__loader__', '__spec__', '__annotations__', '__builtins__', '__file__', )

___included_modules___ = {}
___link_to_real_system_path___ = sys.path
class HackySystemPathList(list):
    @property
    def __iter__(self,):
        # return the injected list
        output = super().__iter__
        # but replace this hacky list with the actual normal path list after it is called 1 time
        sys.path = ___link_to_real_system_path___
        return output

# class HackySystemModules(dict):
#     def __getitem__(self, item):
#         print('getting item',item)
#         # return the injected list
#         return super().__getitem__(item)

#     def __setitem__(self, *items):
#         print('setting item',*items)
#         try:
#             upstack = 1
#             caller_relative_filepath = inspect.stack()[upstack][1]
#             parent_path = dirname(abspath(caller_relative_filepath))
#             print('parent_path = ', parent_path)
#         except:
#             print('failed to get upstack')
#         # return the injected list
#         return super().__setitem__(*items)

# sys.modules = HackySystemModules(sys.modules)

def my_globals():
    return globals()

def file(path, globals=None):
    global ___link_to_real_system_path___
    global ___included_modules___
    '''Use a relative or absolute path to import all of the globals from that file into the current file
    This will not run code more than once, even if it is included multiple times

    :param str path: The path to the file you want to include
    :param int globals: put globals() unless you know what you're doing
    
    :return module: The module object created from importing the file
    Usage::
      >>> import include
      >>> include.file('./folder/file.py', globals())
      >>> # you now have access to all the funcs/vars from 'file.py'
    '''
    your_globals = globals
    absolute_import_path = None
    is_absolute_path = isabs(path)
    if is_absolute_path:
        absolute_import_path = path
    else:
        parent_path = None
        the_filepath_was_in_globals = type(your_globals) == dict and type(your_globals.get("__file__", None)) == str
        # if they provide a path
        if the_filepath_was_in_globals:
            parent_path = dirname(your_globals['__file__'])
        # if this is being run inside a repl, use cwd
        elif sys.path[0] == '':
            parent_path = os.getcwd()
        # try to get it from inspect
        else:
            upstack = 1
            caller_relative_filepath = inspect.stack()[upstack][1]
            parent_path = dirname(abspath(caller_relative_filepath))
        
        absolute_import_path = join(parent_path, path)
    
    # normalize before using
    absolute_import_path = abspath(normpath(absolute_import_path))
    
    # ensure this is a dict
    your_globals = your_globals if type(your_globals) == dict else {}
    
    #
    # error handling
    #
    if not isfile(absolute_import_path):
        if is_absolute_path:
            raise Exception(textwrap.dedent('''
            
            
            in: include.file("'''+path+'''")
            I don't see a file for that path, which I believe is an absolute file path
            '''))
        else:
            header = textwrap.dedent('''
                
                in: include.file("'''+path+'''")
                I don't see a file for that path, however
                - I think that is a relative path
            ''')
            
            if the_filepath_was_in_globals:
                source_of_parent = ""
                raise Exception(header+textwrap.dedent('''
                - I found a '__file__' key in the globals argument, e.g. include.file(path, globals)
                - I used that __file__ to resolve the path to get the absolute path
                - the resolved absolute path was this: "'''+absolute_import_path+'''"
                - that is where I couldn't find a file
                '''))
            else:
                raise Exception(header+textwrap.dedent('''
                - I didn't see a str value for '__file__' in the globals argument, e.g. include.file(path, globals)
                - So instead I tried finding your directory by searching up the inspect path
                - the resolved absolute path was this: "'''+absolute_import_path+'''"
                - that is where I couldn't find a file
                '''))
    
    # if the module was cached
    if absolute_import_path in ___included_modules___ and type(___included_modules___) == ModuleClass:
        module_as_dict = ___included_modules___[absolute_import_path]
    else:
        # FIXME: check for periods in the filename, as they will (proabably) be interpeted as sub-module attributes and break the import
        # get the python file name without the extension
        filename, file_extension = os.path.splitext(basename(absolute_import_path))
        # add a wrapper to the sys path, because modifying it directly would cause polltion/side effects
        # this allows us to import the module from that absolute_import_path 
        # this hacked list will reset itself immediately after the desired file is imported
        ___link_to_real_system_path___ = sys.path
        sys.path = HackySystemPathList([ dirname(absolute_import_path) ])
        
        # make room for the new module
        module_before_replacement = None
        if filename in sys.modules:
            module_before_replacement = sys.modules[filename]
            del sys.modules[filename]
            
        # import the actual module
        module = importlib.import_module(filename)
        module_as_dict = vars(module)
        # save the module to be in our cache
        ___included_modules___[absolute_import_path] = module_as_dict
        # restore the old module if there was one
        if module_before_replacement:
            sys.modules[filename] = module_before_replacement
        else:
            # don't save included modules on the sys.modules at all
            del sys.modules[filename]
    
    # cram the new module into your_globals
    for each in module_as_dict:
        if each not in dont_override:
            your_globals[each] = module_as_dict[each]
    
    return module