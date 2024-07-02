import os
from contextlib import contextmanager
@contextmanager
def enter_dir(newdir):
    prevdir = os.getcwd()
    try:
        yield os.chdir(newdir)
    finally:
        os.chdir(prevdir)


@contextmanager
def change_dir(newdir):
    prevdir = os.getcwd()
    try:
        yield os.chdir(os.path.expanduser(newdir))
    finally:
        os.chdir(prevdir)