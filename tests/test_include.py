from __future__ import absolute_import
import os
import sh
import subprocess
import unittest

try:
    from tempfile import TemporaryDirectory
except ImportError:
    import contextlib
    import shutil
    import tempfile

    @contextlib.contextmanager
    def TemporaryDirectory():
        dirpath = tempfile.mkdtemp()
        yield dirpath
        shutil.rmtree(dirpath)

lib_code = '''# lib.py
def hello():
    return 'world'
'''

app_code_template = '''
from include import include
#import sys
try:
    lib = include('{}')
    print(lib.hello())
except Exception as e:
    print(str(e))
    #sys.exit(1)
'''

garbage = '''lfasjd'''

def app_setup(path, lib_relative):
    place_at_path(app_code_template.format(lib_relative), path)

def lib_setup(path):
    place_at_path(lib_code, path)

def place_at_path(contents, path):
    sh.mkdir('-p', os.path.dirname(path))
    with open(path, 'w') as f:
        f.write(contents)

class RequireTest(unittest.TestCase):

    def test_sibling(self):
        with TemporaryDirectory() as tmp:

            app = os.path.join(tmp, 'app.py')
            app_setup(app, './lib.py')

            lib = os.path.join(tmp, 'lib.py')
            lib_setup(lib)

            stdout = subprocess.check_output(['python', app])
            self.assertEqual(stdout, b'world\n')

    def test_descendant(self):
        with TemporaryDirectory() as tmp:
            app = os.path.join(tmp, 'app.py')
            app_setup(app, './directory/lib.py')

            lib = os.path.join(tmp, 'directory', 'lib.py')
            lib_setup(lib)

            stdout = subprocess.check_output(['python', app])
            self.assertEqual(stdout, b'world\n')

    def test_ancestor(self):
        with TemporaryDirectory() as tmp:
            app = os.path.join(tmp, 'directory', 'app.py')
            app_setup(app, '../lib.py')
            lib = os.path.join(tmp, 'lib.py')
            lib_setup(lib)

            stdout = subprocess.check_output(['python', app])
            self.assertEqual(stdout, b'world\n')

    def test_arbitrary(self):
        with TemporaryDirectory() as tmp:
            app = os.path.join(tmp, 'directory', 'app.py')
            app_setup(app, '../folder/lib.py')
            lib = os.path.join(tmp, 'folder', 'lib.py')
            lib_setup(lib)

            stdout = subprocess.check_output(['python', app])
            self.assertEqual(stdout, b'world\n')

    def test_absolute(self):
        with TemporaryDirectory() as tmp:
            app = os.path.join(tmp, 'app.py')
            lib = os.path.join(tmp, 'lib.py')
            app_setup(app, lib)
            lib_setup(lib)

            stdout = subprocess.check_output(['python', app])
            self.assertEqual(stdout, b'world\n')

    def test_package(self):
        with TemporaryDirectory() as tmp:
            app = os.path.join(tmp, 'app.py')
            lib = os.path.join(tmp, 'directory', '__init__.py')
            app_setup(app, './directory')
            lib_setup(lib)

            stdout = subprocess.check_output(['python', app])
            self.assertEqual(stdout, b'world\n')

    def test_no_file(self):
        with TemporaryDirectory() as tmp:
            app = os.path.join(tmp, 'app.py')
            app_setup(app, './lib.py')
            lib = os.path.join(tmp, 'lib.py')

            stdout = subprocess.check_output(['python', app])
            self.assertEqual(stdout, str.encode('No module at {}\n'.format(lib)))

    def test_invalid_python(self):
        with TemporaryDirectory() as tmp:
            app = os.path.join(tmp, 'app.py')
            app_setup(app, './lib.py')
            lib = os.path.join(tmp, 'lib.py')
            place_at_path(garbage, lib)

            stdout = subprocess.check_output(['python', app])
            self.assertEqual(stdout, str.encode("name '{}' is not defined\n".format(garbage)))

if __name__ == '__main__':
    unittest.main()
