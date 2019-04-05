import sys
import os
import glob

print(__file__)

# +
## glob pattern that searches all python files not naming X.py
# -

glob.glob('*.py')

glob.glob('[!__init]*.py')
