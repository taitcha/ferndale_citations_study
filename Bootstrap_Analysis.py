
import datetime
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import numpy as np
import matplotlib.pyplot as plt

filetype = ".csv"

def runBootstrap(citations):
    citationsA = citations.copy()

    return