import numpy as np
import pandas as pd

# initial data prep
def getAgeGroupList(df, ageCol="age"):
    return([
        (df[ageCol] < 50) & (df["sex"] == "Male"), 
        (df[ageCol] >= 50) & (df[ageCol] <= 64) & (df["sex"] == "Male"), 
        (df[ageCol] > 64) & (df["sex"] == "Male"),
        (df[ageCol] < 50) & (df["sex"] == "Female"), 
        (df[ageCol] >= 50) & (df[ageCol] <= 64) & (df["sex"] == "Female"), 
        (df[ageCol] > 64) & (df["sex"] == "Female"),
    ])
    
def getAgeThresholds(inputDf, selectedColumns):
    inputDf = inputDf[selectedColumns + ["age_group", "sex"]]
    return inputDf.groupby(["age_group", "sex"]).quantile([0.25, 0.75])

def checkListClean(biomarkersList):
    if type(biomarkersList) is list:
        return biomarkersList
    if any(biomarkersList.str.contains("age")):
        return biomarkersList.drop(["age_group"])
    
# bhs score (original)
def scoreDf(inputDf, biomarkersList):
    for ageGroup in getAgeGroupList(inputDf):
        for col in biomarkersList:
            inputDf.loc[ageGroup,f"{col[:-4]}_score"] = \
                np.select(
                    [inputDf.loc[ageGroup,col] > inputDf[ageGroup][col].quantile([0.75]).values[0],
                    inputDf.loc[ageGroup,col] <= inputDf[ageGroup][col].quantile([0.75]).values[0]],                   
                    [1.0, 0.0], default=np.nan)

    return inputDf

def scoreDfReverse(inputDf, biomarkersList):
    for ageGroup in getAgeGroupList(inputDf):
        for col in biomarkersList:
            inputDf.loc[ageGroup,f"{col[:-4]}_score"] = \
                np.select(
                    [inputDf.loc[ageGroup,col] < inputDf[ageGroup][col].quantile([0.25]).values[0],
                    inputDf.loc[ageGroup,col] >= inputDf[ageGroup][col].quantile([0.25]).values[0]],                   
                    [1.0, 0.0], default=np.nan)

    return inputDf


def biomarkerScore(inputDf_t0, inputDf_t1, biomarkersList_t0,
                    biomarkersList_t1, 
                    biomarker_lower_quartile_scored=False,
                    reverse=False):

    biomarkersList_t0 = checkListClean(biomarkersList_t0)
    biomarkersList_t1 = checkListClean(biomarkersList_t1)
    # if (biomarker_lower_quartile_scored is False) and (reverse is False): 
    if reverse is False:

        inputDf_t0 = scoreDf(inputDf_t0, biomarkersList_t0)
        inputDf_t1 = scoreDf(inputDf_t1, biomarkersList_t1)

        # manually calculate baseline score
        for ageGroup in getAgeGroupList(inputDf_t1):
            for col in biomarkersList_t1:
                inputDf_t1.loc[ageGroup,f"{col[:-4]}_score_b"] = \
                    np.select(
                        [inputDf_t1.loc[ageGroup,col] > inputDf_t0[ageGroup][col.replace("1.0","0.0")].quantile([0.75]).values[0],
                        inputDf_t1.loc[ageGroup,col] <= inputDf_t0[ageGroup][col.replace("1.0","0.0")].quantile([0.75]).values[0]],                   
                        [1.0, 0.0],
                        default=np.nan)

        return inputDf_t0, inputDf_t1

    # if (biomarker_lower_quartile_scored is False) and (reverse is True):
    if reverse is True:

        inputDf_t0 = scoreDfReverse(inputDf_t0, biomarkersList_t0)
        inputDf_t1 = scoreDfReverse(inputDf_t1, biomarkersList_t1)

        for ageGroup in getAgeGroupList(inputDf_t1):
            for col in biomarkersList_t1:
                inputDf_t1.loc[ageGroup,f"{col[:-4]}_score_b"] = \
                    np.select(
                        [inputDf_t1.loc[ageGroup,col] < inputDf_t0[ageGroup][col.replace("1.0","0.0")].quantile([0.25]).values[0],
                        inputDf_t1.loc[ageGroup,col] >= inputDf_t0[ageGroup][col.replace("1.0","0.0")].quantile([0.25]).values[0]],                   
                        [1.0, 0.0],
                        default=np.nan)

        return inputDf_t0, inputDf_t1



# subsystem contrib calculation
def count_scores(row):
    counted = row.count("_score")
    if counted == 5:
        return "None"
    elif counted >= 2:
        return "Mixed"
    elif counted == 1:
        return row
    else:
        return np.nan

