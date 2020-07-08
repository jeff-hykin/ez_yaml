from __future__ import absolute_import

generic_globals = dict(globals())
generic_globals.update(dict(locals()))

import inspect
import os

__ALL_MODULES__ = {}
# TODO: add a check for circular inports
def include(relative_path_to_other_file, your_globals=None):
    '''Import all of the globals/locals from a file into the current file
    This will not run code more than once, even if it is included multiple times
    As of version 0.0.1, there is no circular depencency checker.

    :param str relative_path_to_other_file: The path to the file you want to include
    :param int your_globals: put globals() unless you know what you're doing

    Usage::
      >>> import include
      >>> include.include('file.py', globals())
      >>> # you now have access to all the funcs/vars from 'file.py'
    '''
    if not your_globals.get("__file__", None):
        your_globals["__file__"] = os.getcwd() + "/<REPL>"
    path_to_file = os.path.abspath(os.path.join(os.path.dirname(your_globals["__file__"]), relative_path_to_other_file))
    
    # init your_globals if the argument wasn't included
    if your_globals == None:
        your_globals = {}
    
    # if file hasn't been loaded yet
    if not (path_to_file in __ALL_MODULES__):
        their_globals = dict(generic_globals)
        # set their path so things don't break
        their_globals['__file__'] = path_to_file
        output = ""
        with open(path_to_file,'r') as f:
            output = f.read()
        try:
            exec(output, their_globals, their_globals)
        except Exception as error:
            import traceback
            traceback_str = traceback.format_exc()
            raise Exception(traceback_str + "\n\nError on: " + path_to_file + ":" + str(error.__traceback__.tb_next.tb_lineno) + "\nfrom the include(\'"+relative_path_to_other_file+"\')")
        __ALL_MODULES__[path_to_file] = their_globals
    
    # combine their globals into your globals
    their_globals = __ALL_MODULES__[path_to_file]
    # remove the one thing that should be unique to their file
    if "__file__" in their_globals:
        del their_globals["__file__"]
    # put their globals into your file
    your_globals.update(their_globals)
    # return the globals for good measure
    return your_globals