import numpy as np

def summary(x):
    funcs = dict(
        Minimum = np.min, 
        Maxipmum = np.max, 
        Mean = np.mean)
    
    for label, func in funcs.items():
        value = func(x)
        print("%10s: %10.2f" % (label, value))