from __future__ import absolute_import

generic_globals = dict(globals())
generic_locals  = dict(locals())

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
    path_to_file = resolve_path(relative_path_to_other_file, upstack=1)
    
    # init your_globals if the argument wasn't included
    if your_globals == None:
        your_globals = {}
    
    # if file hasn't been loaded yet
    if not (path_to_file in __ALL_MODULES__):
        their_locals = dict(generic_globals)
        their_globals = dict(generic_locals)
        output = ""
        with open(path_to_file,'r') as f:
            output = f.read()
        try:
            exec(output, their_globals, their_locals)
        except Exception as error:
            import traceback
            traceback_str = traceback.format_exc()
            raise Exception(traceback_str + "\n\nError on: " + path_to_file + ":" + str(error.__traceback__.tb_next.tb_lineno) + "\nfrom the include(\'"+relative_path_to_other_file+"\')")
        their_globals.update(their_locals)
        __ALL_MODULES__[path_to_file] = their_globals
    
    # combine their globals into your globals
    their_globals = __ALL_MODULES__[path_to_file]
    # put their globals into your file
    your_globals.update(their_globals)
    # return the globals for good measure
    return your_globals

def resolve_path(path, upstack=0):
    # this function was pulled from https://github.com/pcattori/require.py 
    # you can tell because it has good docstrings
    '''Resolve a path to an absolute path by taking it to be relative to the source
    code of the caller's stackframe shifted up by `upstack` frames.

    :param str path: Filesystem path
    :param int upstack: Number of stackframes upwards from caller's stackframe
    to act as relative point.

    #: TODO Usage example is not great on REPL...

    Usage::
      >>> import require # at /home/require
      >>> require.resolve_path('file.txt')
      '/home/require/file.txt'
    '''
    if os.path.isabs(path):
        return path
    # get absolute path by rooting path with calling script directory
    # TODO guard rails for upstack? 
    caller_relative_filepath = inspect.stack()[upstack + 1][1]
    caller_root = os.path.dirname(os.path.abspath(caller_relative_filepath))
    return os.path.abspath(os.path.join(caller_root, path))
