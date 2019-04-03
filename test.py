import sys
import os

name = "John Doe"
age = 30

# best way to write multiline strings
string = ("%s (%s), I have some more information for you. "
          "Click here.") % (name, age)
print(string)

for dirpath, dirnames, filenames in os.walk('dispypkg'):
    print("%20s %20s %20s" % (dirpath, dirnames, filenames))

print(__file__)