#!/usr/bin/env python
# coding: utf-8

# """
# looking at behaviours for univariate analysis 
# against different bhs scores
# also knn vs no imputation
# """

import pandas as pd
import matplotlib
from functions.univariate_linear import getUnivariatePlotDf, getUnivariateResults
from functions.ukbb_cleaning import relabelNames, getCategory
from functions.loadPipelineProducts import getProductFromDag, tidyOutputName
from functions.pipelineVariables import upstreamList, studyList
matplotlib.rcParams['font.family'] = ["DejaVu Sans"]

# %% tags=["parameters"]
upstream = ["Compute DASH"]
product = None

# %%
recodingDict = pd.read_excel("data/combined_recoding_dict.xlsx")

exclusionList = ["glycated_haemoglobin","HDL_cholesterol","LDL_direct","triglycerides","systolic_bp","diastolic_bp",
 "pulse_rate","c.reactive_protein","IGF1","creatinine", "cystatin_C", "alanine_aminotransferase", "urea", "heterozygosity",
 "mean_corpuscular_volume", "aspartate_aminotransferase","gamma_glutamyltransferase", "score", "eid", "delta", "age_group"] + \
["FEV", "FVC", "PEF", "_NG"] + ["T_S", "eosinophil", "erythrocyte", "neutrophil", "reticulocyte", "aemoglobin"] + \
["lymphocyte", "basophil", "monocyte", "rbc", "platelet", "platlet", "sphered", "leukocyte"] + \
["SHGB", "sodium", "microalbumin", "protein", "potassium", "alkaline", "calcium", "phosphate", "urate", "vitamin_D"] + \
["albumin", "glucose", "bilirubin", "oestradiol", "rheumatoid", "cholesterol", "testosterone"]

# %%
def univariateAnalysis(df, exclusionList, recodingDict):
    univariateList = df.columns[~df.columns.str.contains("|".join(exclusionList))]
    univariateList = univariateList[univariateList.str.contains(".0.0", regex=False)]
    confounderVars = " + bhs_score.0.0"
    
    deltaBHS = getUnivariatePlotDf(df, univariateList, "delta_bhs", adjustments=confounderVars)
    deltaBHS_b = getUnivariatePlotDf(df, univariateList, "delta_bhs_b", adjustments=confounderVars)
    deltaBiomarker = getUnivariatePlotDf(df, univariateList, "delta_biomarker_bhs", adjustments=confounderVars)

    deltaBHS = relabelNames(deltaBHS, recodingDict)
    deltaBHS_b = relabelNames(deltaBHS_b, recodingDict)
    deltaBiomarker = relabelNames(deltaBiomarker, recodingDict)

    deltaBHS = getCategory(deltaBHS, recodingDict)
    deltaBHS_b = getCategory(deltaBHS_b, recodingDict)
    deltaBiomarker = getCategory(deltaBiomarker, recodingDict)

    return deltaBHS, deltaBHS_b, deltaBiomarker


# %%
for studyType, studyName in zip(studyList, upstreamList):
    df = pd.read_parquet(getProductFromDag("Compute DASH")[studyType])
    print(studyName)
    deltaBHS, deltaBHS_b, deltaBiomarker = univariateAnalysis(df, exclusionList, recodingDict) 

    # save outputs
    baseOutputPath = f"output/03_univariate/tables/{tidyOutputName(studyName, 'Calculate')}"
    deltaBHS.to_csv(f"{baseOutputPath}_lm_deltabhs.csv", index=False)
    deltaBHS_b.to_csv(f"{baseOutputPath}_lm_deltabhs_b.csv", index=False)
    deltaBiomarker.to_csv(f"{baseOutputPath}_lm_deltabiomarker.csv", index=False)

    # sanity checks
    print(deltaBHS[(deltaBHS["pval"]!=0)].iloc[:,0:4].tail())
    print(deltaBiomarker[(deltaBiomarker["pval"]!=0)].iloc[:,0:4].tail())
