"""
    pull data for sharp stability
    package wants it in one-hot-encoded
    x & y format
"""

import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from functions.loadPipelineProducts import getProductFromDag, tidyOutputName
from functions.pipelineVariables import upstreamList, studyList
import gc

# %% tags=["parameters"]
upstream = ["Compute DASH"]
product = None

#%%
def getSharpList(inputDf):

    exclusionList = ["glycated_haemoglobin","HDL_cholesterol","LDL_direct","triglycerides","systolic_bp","diastolic_bp",
    "pulse_rate","c.reactive_protein","IGF1","creatinine", "cystatin_C", "alanine_aminotransferase", "urea", "heterozygosity",
    "mean_corpuscular_volume", "aspartate_aminotransferase","gamma_glutamyltransferase", "score", "eid", "delta", "age_group"] + \
    ["FEV", "FVC", "PEF", "_NG"] + ["T_S", "eosinophil", "erythrocyte", "neutrophil", "reticulocyte", "aemoglobin"] + \
    ["lymphocyte", "basophil", "monocyte", "rbc", "platelet", "platlet", "sphered", "leukocyte"] + \
    ["SHGB", "sodium", "microalbumin", "protein", "potassium", "alkaline", "calcium", "phosphate", "urate", "vitamin_D"] + \
    ["albumin", "glucose", "bilirubin", "oestradiol", "rheumatoid", "cholesterol", "testosterone"]

    noxList = ["NO2_2005.0.0", "NO2_2006.0.0", "NO2_2007.0.0", "NO2_2010.0.0", "NO_2010.0.0"]
    inputDf["meanNOx.0.0"] = inputDf[noxList].mean(axis=1)

    sharpList = inputDf.columns[~inputDf.columns.str.contains("|".join(exclusionList))]
    sharpList = sharpList[sharpList.str.contains(".0.0", regex=False)]
    sharpList = sharpList.drop(noxList)
    sharpList = sharpList.append(pd.Index(["bhs_score.0.0","DASH_SCORE"]))

    return inputDf, sharpList
# %%

def saveSharpFiles(inputDf, sharpList, filename):
    X = pd.get_dummies(inputDf[sharpList])
    X = X.dropna(axis=1, thresh=0.7*len(X))
    print(X.shape)

    imp_mode = SimpleImputer(missing_values=np.nan, strategy="most_frequent")
    imp_X = imp_mode.fit_transform(X)
    imp_X_df = pd.DataFrame(imp_X, columns=X.columns)

    imp_X_df.to_parquet(
        f"output/04_lasso_multivariate/data/{tidyOutputName(filename, 'Calculate')}_x_one_hot_data.parquet",
        index=False)

    inputDf[["delta_bhs", "delta_bhs_b", "delta_biomarker_bhs"]].to_parquet(
        f"output/04_lasso_multivariate/data/{tidyOutputName(filename, 'Calculate')}_y_data.parquet",
        index=False)


#%% main
def getSharpDataFiles(inputDfPath, studyName):
    inputDf = pd.read_parquet(inputDfPath)
    inputDf, newSharpList = getSharpList(inputDf)
    saveSharpFiles(inputDf, newSharpList, studyName)

for studyType, studyName in zip(studyList, upstreamList):
    getSharpDataFiles(getProductFromDag("Compute DASH")[studyType], studyName)
    del studyType, studyName
    gc.collect()
