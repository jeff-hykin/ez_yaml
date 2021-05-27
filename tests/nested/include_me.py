import os
import sys
import include 

include.file("../other_nested/include_me.py", globals())

def hello():
    print('this should be ..."nested/include_me.py" ', __file__)
    print('hello')