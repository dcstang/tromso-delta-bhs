# store important quartiles for BHS calculations
# Date: 23 Feb
# Author: David Tang

import pandas as pd
import numpy as np
import os
import json
import pathlib


def getQuartile(dfCol):
    return np.nanpercentile(dfCol, 75)

def initThresholdStorage(suffix=""):    
    if os.path.exists("Outputs/"):
        pass
    else: 
        os.mkdir("Outputs/")
        print("'Outputs' directory created!")

    quartileThresDict = dict.fromkeys([
        "Endocrine",
        "Metabolic",
        "Cardiovascular",
        "Inflammatory",
        "Liver",
        "Kidney"
    ])

    if not os.path.isfile("Outputs" + "/quartileThresholds" + suffix + ".json"):
        with open("Outputs" + "/quartileThresholds" + suffix + ".json", "w") as fp:
            json.dump(quartileThresDict, fp, indent=4)
        print("Initialised threshold dictionary ...")

def updateDictStorage(system, quartile):
    if not list(pathlib.Path("Ouputs").glob("*.json")):
        initThresholdStorage()
        