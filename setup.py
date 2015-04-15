"""Setup the program"""

from setuptools import setup

setup(
    name="text-rearranger",
    version="1.0",
    description="a program that randomly redistributes the contents of a stream of text",
    long_description="Text Rearranger is a command-line interface library that gives uses a whopping 52 commands to interact with streams of text. The main usage is re-writing some text based on word topology- that is, the case, leading letter, and length of the word. Other major modes filter the output based on certain words or inspect the internal representation of itself.",
    url="https://github.com/nikkisquared/Text-Rearranger",
    author="Nikki Bee",
    author_email="private",
    classifiers=[
    "Development Status :: 5 - Production/Stable",
    "Environment :: Win32 (MS Windows)",
    "Environment :: MacOS X",
    "Environment :: X11 Applications",
    "Intended Audience :: Developers",
    "Intended Audience :: End Users/Desktop",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.7",
    "Topic :: Artistic Software",
    "Topic :: Text Processing",
    "Topic :: Utilities"
    ],
    keywords="random text console",
    packages=[]
)