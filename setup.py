import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "figpie",
    version = "0.0.1",
    author = "Bartosz Piekarski",
    author_email = "mchtrbartoszpiekarski@gmail.com",
    description = ("Simple interactive (con)fig"),
    license = "BSD",
    keywords = "simple interactive configuration",
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)

