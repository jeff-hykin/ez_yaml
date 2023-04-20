# coding: utf-8

import sys
import platform
import pytest
from textwrap import dedent

NO_CLIB_VER = (3, 10)


@pytest.mark.skipif(
    platform.python_implementation() in ['Jython', 'PyPy'],
    reason='Jython throws RepresenterError'
)
def test_load_cyaml():
    print("???????????????????????", platform.python_implementation())
    exec(f"""import {".".join(__name__.split(".")[:-2])}.yaml;ruamel = {".".join(__name__.split(".")[:-2])}""")

    if sys.version_info >= NO_CLIB_VER:
        return
    yaml = ruamel.yaml.YAML(typ='safe', pure=False)
    assert ruamel.yaml.__with_libyaml__

    yaml.load('abc: 1')


@pytest.mark.skipif(sys.version_info >= NO_CLIB_VER
                    or platform.python_implementation() in ['Jython', 'PyPy'],
                    reason='no _PyGC_FINALIZED')
def test_dump_cyaml():
    exec(f"""import {".".join(__name__.split(".")[:-2])}.yaml;ruamel = {".".join(__name__.split(".")[:-2])}""")

    if sys.version_info >= NO_CLIB_VER:
        return
    data = {'a': 1, 'b': 2}
    yaml = ruamel.yaml.YAML(typ='safe', pure=False)
    yaml.default_flow_style = False
    yaml.allow_unicode = True
    buf = ruamel.yaml.compat.StringIO()
    yaml.dump(data, buf)
    assert buf.getvalue() == 'a: 1\nb: 2\n'


@pytest.mark.skipif(
    platform.python_implementation() in ['Jython', 'PyPy'], reason='not avialable'
)
def test_load_cyaml_1_2():
    # issue 155
    exec(f"""import {".".join(__name__.split(".")[:-2])}.yaml;ruamel = {".".join(__name__.split(".")[:-2])}""")

    if sys.version_info >= NO_CLIB_VER:
        return
    assert ruamel.yaml.__with_libyaml__
    inp = dedent("""\
    %YAML 1.2
    ---
    num_epochs: 70000
    """)
    yaml = ruamel.yaml.YAML(typ='safe')
    yaml.load(inp)


@pytest.mark.skipif(
    platform.python_implementation() in ['Jython', 'PyPy'], reason='not available'
)
def test_dump_cyaml_1_2():
    # issue 155
    exec(f"""import {".".join(__name__.split(".")[:-2])}.yaml;ruamel = {".".join(__name__.split(".")[:-2])}""")
    from ruamel.yaml.compat import StringIO

    if sys.version_info >= NO_CLIB_VER:
        return
    assert ruamel.yaml.__with_libyaml__
    yaml = ruamel.yaml.YAML(typ='safe')
    yaml.version = (1, 2)
    yaml.default_flow_style = False
    data = {'a': 1, 'b': 2}
    exp = dedent("""\
    %YAML 1.2
    ---
    a: 1
    b: 2
    """)
    buf = StringIO()
    yaml.dump(data, buf)
    assert buf.getvalue() == exp
