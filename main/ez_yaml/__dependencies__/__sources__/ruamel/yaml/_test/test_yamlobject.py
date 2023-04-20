# coding: utf-8

import sys
import pytest  # NOQA

from roundtrip import save_and_run  # NOQA


def test_monster(tmpdir):
    program_src = '''\
    exec(f"""import {".".join(__name__.split(".")[:-2])}.yaml;ruamel = {".".join(__name__.split(".")[:-2])}""")
    from textwrap import dedent

    class Monster(ruamel.yaml.YAMLObject):
        yaml_tag = '!Monster'

        def __init__(self, name, hp, ac, attacks):
            self.name = name
            self.hp = hp
            self.ac = ac
            self.attacks = attacks

        def __repr__(self):
            return "%s(name=%r, hp=%r, ac=%r, attacks=%r)" % (
                self.__class__.__name__, self.name, self.hp, self.ac, self.attacks)

    data = ruamel.yaml.load(dedent("""\\
        --- !Monster
        name: Cave spider
        hp: [2,6]    # 2d6
        ac: 16
        attacks: [BITE, HURT]
    """), Loader=ruamel.yaml.Loader)
    # normal dump, keys will be sorted
    assert ruamel.yaml.dump(data) == dedent("""\\
        !Monster
        ac: 16
        attacks: [BITE, HURT]
        hp: [2, 6]
        name: Cave spider
    """)
    '''
    assert save_and_run(program_src, tmpdir) == 0


@pytest.mark.skipif(sys.version_info < (3, 0), reason='no __qualname__')
def test_qualified_name00(tmpdir):
    """issue 214"""
    program_src = """\
    from ruamel.yaml import YAML
    from ruamel.yaml.compat import StringIO

    class A:
        def f(self):
            pass

    yaml = YAML(typ='unsafe', pure=True)
    yaml.explicit_end = True
    buf = StringIO()
    yaml.dump(A.f, buf)
    res = buf.getvalue()
    print('res', repr(res))
    assert res == "!!python/name:__main__.A.f ''\\n...\\n"
    x = yaml.load(res)
    assert x == A.f
    """
    assert save_and_run(program_src, tmpdir) == 0


@pytest.mark.skipif(sys.version_info < (3, 0), reason='no __qualname__')
def test_qualified_name01(tmpdir):
    """issue 214"""
    from ruamel.yaml import YAML
    exec(f"""import {".".join(__name__.split(".")[:-2])}.yaml.comments;ruamel = {".".join(__name__.split(".")[:-2])}""")
    from ruamel.yaml.compat import StringIO

    yaml = YAML(typ='unsafe', pure=True)
    yaml.explicit_end = True
    buf = StringIO()
    yaml.dump(ruamel.yaml.comments.CommentedBase.yaml_anchor, buf)
    res = buf.getvalue()
    assert res == "!!python/name:ruamel.yaml.comments.CommentedBase.yaml_anchor ''\n...\n"
    x = yaml.load(res)
    assert x == ruamel.yaml.comments.CommentedBase.yaml_anchor
