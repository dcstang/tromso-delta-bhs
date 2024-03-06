# Functions for trajectory clustering processing
# 1. pulling data into numpy timepoint
# 2. linear interpolation for one missing val in timeseries
# April 2022 - David Tang

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

def getDates(t2, t3, t4, t5, t6, t7):
    return np.array([t2.to_numpy(), t3.to_numpy(), 
                    t4.to_numpy(), t5.to_numpy(), 
                    t6.to_numpy(), t7.to_numpy()])

def getTS(t2, t3, t4, t5, t6, t7):
    return np.array([t2, t3, t4, t5, t6, t7])


def fill_nan(A):
    '''
    interpolate to fill nan values
    '''
    inds = np.arange(A.shape[0])
    good = np.where(np.isfinite(A))
    f = interp1d(inds[good], A[good],bounds_error=False)
    B = np.where(np.isfinite(A),A,f(inds))
    return B