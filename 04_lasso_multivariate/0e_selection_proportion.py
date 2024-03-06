#!/usr/bin/env python
# coding: utf-8
# X vs Y selection proportion between scores

#%% 

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import time
import os.path

from functions.ukbb_cleaning import cleanMergeCat
from functions.loadPipelineProducts import tidyOutputName
matplotlib.rcParams['font.family'] = ["DejaVu Sans"]

# %% tags=["parameters"]
upstream = ["Sharp stability selection"]
product = None

rFileList = [
    "bhs_complete_cases",
    "bhs_complete_cases_n_lower_quartile_scored",
    "bhs_knn_impute_n_lower_quartile_scored",
    "bhs_knn_impute_only",
    "bhs_complete_cases_n_pca_bhs",
    "bhs_knn_impute_n_pca_bhs",
    "bhs_complete_cases_n_pca_subsystem_bhs",
    "bhs_knn_impute_n_pca_subsystem_bhs",
    "bhs_complete_cases_n_pca_subsystem_bhs_scaled",
    "bhs_knn_impute_n_pca_subsystem_bhs_scaled",
]

# workaround, quick check of files contained in folder
checkFileList = ["delta_bhs_b_" + x for x in rFileList] + \
    ["delta_bhs_" + x for x in rFileList] + ["delta_biomarker_" + x for x in rFileList]

output_folder = "/rds/general/user/dt20/home/BHS/output/04_lasso_multivariate/tables/"
a_exist = [f for f in checkFileList if os.path.isfile(output_folder)]

if len(a_exist) == len(checkFileList):
    pass
else:
    print(len(checkFileList) - len(a_exist))
    time.sleep(4*60*60) # wait 4 hour for prior pipeline to finish

#%% 

def highlightThresholdBars(plotDf, threshold_criteria):
    return ['skyblue' if x >= threshold_criteria else 'lightgrey' for x in plotDf.pctSelected]

def plotSelectionProportion(plotDf, plotDf2, 
                            dbhs_threshold, dbiomarker_threshold,
                            saveFileName, varNumb=9):    
    
    plotDf = plotDf.iloc[0:varNumb,:]
    plotDf2 = dbiomarker.iloc[0:varNumb,:]

    plotDfList = [plotDf, plotDf2]
    thresholdList = [dbhs_threshold, dbiomarker_threshold]
    titleList = ["dBHS", "dBiomarkerBHS"]

    fig, axes = plt.subplots(figsize=(8,4.5*2), nrows=2,
                  sharex=True, gridspec_kw={"hspace":0.2})

    for idx, (df, threshold) in enumerate(zip(plotDfList, thresholdList)): 
        sns.barplot(y="FigureName", x="pctSelected", data=df, ax=axes[idx],
                            palette=highlightThresholdBars(df, threshold[1][0]))
        axes[idx].set_title(titleList[idx])
        axes[idx].axvline(x=threshold[1][0])

    for axi in axes:
        axi.set_xlabel("Selection proportion")
        axi.set(ylabel=None)
    
    saveFileName = tidyOutputName(saveFileName, "Calculate")
    prefix_savepath="/rds/general/user/dt20/home/BHS/output/04_lasso_multivariate/selection_props/"
    plt.savefig(f"{prefix_savepath}selection_proportion_{saveFileName}.png", dpi=350, bbox_inches="tight")

# %%

rFileList = [
    "bhs_complete_cases",
    "bhs_complete_cases_n_lower_quartile_scored",
    "bhs_knn_impute_n_lower_quartile_scored",
    "bhs_knn_impute_only",
    "bhs_complete_cases_n_pca_bhs",
    "bhs_knn_impute_n_pca_bhs",
    "bhs_complete_cases_n_pca_subsystem_bhs",
    "bhs_knn_impute_n_pca_subsystem_bhs",
    "bhs_complete_cases_n_pca_subsystem_bhs_scaled",
    "bhs_knn_impute_n_pca_subsystem_bhs_scaled",
]

recoding_dict = pd.read_excel("/rds/general/user/dt20/home/BHS/data/combined_recoding_dict.xlsx")

for studyType in rFileList:
    print(studyType)
    prefix_path="/rds/general/user/dt20/home/BHS/output/04_lasso_multivariate/tables/"
    
    dbhs = pd.read_csv(f"{prefix_path}delta_bhs_{studyType}_variable_selection_one_hot.csv")
    dbiomarker = pd.read_csv(f"{prefix_path}delta_biomarker_{studyType}_variable_selection_one_hot.csv")

    dbhs = cleanMergeCat(dbhs, recoding_dict)
    dbiomarker = cleanMergeCat(dbiomarker, recoding_dict)

    # sharp selection threshold 
    dbhs_threshold = pd.read_csv(f"{prefix_path}delta_bhs_{studyType}_lambdaPi_one_hot.txt",
                            delim_whitespace=True, header=None)
    dbiomarker_threshold = pd.read_csv(f"{prefix_path}delta_biomarker_{studyType}_lambdaPi_one_hot.txt",
                            delim_whitespace=True, header=None)
    
    plotSelectionProportion(dbhs, dbiomarker, dbhs_threshold, dbiomarker_threshold, studyType, 12)

