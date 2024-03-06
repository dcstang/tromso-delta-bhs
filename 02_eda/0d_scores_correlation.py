#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from scipy.stats import pearsonr
import numpy as np
from functions.pipelineVariables import upstreamList, studyList
from functions.loadPipelineProducts import getProductFromDag, tidyOutputName

# %% tags=["parameters"]
upstream = ['Run tableOnes']
product = None

# %% main function 
def scoresCorrelationTable(inputDf, bhsTypeName):

    sexList = ["Overall", "Male", "Female"]
    ageList = ["-", "<50", "50-64", ">64"]
    outputList = []

    for sexType in sexList:
        for ageType in ageList:
            tempList = [bhsTypeName, sexType, ageType]

            if (sexType=="Overall") & (ageType=="-"):
                tempList.extend(list(np.around(
                    pearsonr(inputDf['delta_bhs'], inputDf['delta_biomarker_bhs']),2)))
            elif (sexType=="Overall") & (ageType=="<50"):
                tempList.extend(list(np.around(pearsonr(
                        inputDf[inputDf["age.0.0"]<50]['delta_bhs'], 
                        inputDf[inputDf["age.0.0"]<50]['delta_biomarker_bhs']),2)))
            elif (sexType=="Overall") & (ageType=="50-64"):
                tempList.extend(list(np.around(pearsonr(
                        inputDf[(inputDf["age.0.0"]>=50) & (inputDf["age.0.0"]<=64)]['delta_bhs'], 
                        inputDf[(inputDf["age.0.0"]>=50) & (inputDf["age.0.0"]<=64)]['delta_biomarker_bhs']),2)))
            elif (sexType=="Overall") & (ageType==">64"):
                tempList.extend(list(np.around(pearsonr(
                        inputDf[inputDf["age.0.0"]>64]['delta_bhs'], 
                        inputDf[inputDf["age.0.0"]>64]['delta_biomarker_bhs']),2)))
            elif (sexType!="Overall") & (ageType=="-"):
                tempList.extend(list(np.around(pearsonr(
                        inputDf[(inputDf["sex"]==sexType)]['delta_bhs'], 
                        inputDf[(inputDf["sex"]==sexType)]['delta_biomarker_bhs']),2)))
            elif (sexType!="Overall") & (ageType=="<50"):
                tempList.extend(list(np.around(pearsonr(
                        inputDf[(inputDf["age.0.0"]<50) & (inputDf["sex"]==sexType)]['delta_bhs'], 
                        inputDf[(inputDf["age.0.0"]<50) & (inputDf["sex"]==sexType)]['delta_biomarker_bhs']),2)))
            elif (sexType!="Overall") & (ageType=="50-64"):
                tempList.extend(list(np.around(pearsonr(
                        inputDf[(inputDf["age.0.0"]>=50) & (inputDf["age.0.0"]<=64)]['delta_bhs'], 
                        inputDf[(inputDf["age.0.0"]>=50) & (inputDf["age.0.0"]<=64)]['delta_biomarker_bhs']),2)))
            elif (sexType!="Overall") & (ageType==">64"):
                tempList.extend(list(np.around(pearsonr(
                        inputDf[(inputDf["age.0.0"]>64) & (inputDf["sex"]==sexType)]['delta_bhs'], 
                        inputDf[(inputDf["age.0.0"]>64) & (inputDf["sex"]==sexType)]['delta_biomarker_bhs']),2)))
            else: tempList.extend(["-", "-"])
            outputList.append(tempList)

    return pd.DataFrame(data=outputList,
                columns=["BHS Type","Sex strata","Age strata", "pearsonr","pval"])


# %% run everything using output/names from pipeline 

# gather outputs
outputList = []
for studyType, studyName in zip(studyList, upstreamList):
    df = pd.read_parquet(getProductFromDag("Compute DASH")[studyType])
    correlationTable = scoresCorrelationTable(df, studyName)
    outputList.append(correlationTable)
    print(studyName, correlationTable)

# save all now in one sheet 
excelOutputPath = "output/02_eda/tables/all_bhs_types_correlation_scores.xlsx"
writer = pd.ExcelWriter(excelOutputPath, engine="openpyxl")
for idx, outputDf in enumerate(outputList):
    outputList[idx].to_excel(writer, sheet_name=f"{idx}_{upstreamList[idx]}")
writer.close()
print(f"Saved at {excelOutputPath}")