#!/usr/bin/env python
# coding: utf-8

"""
Generate Table 1 for population with repeated measures
"""

import pandas as pd
import numpy as np
from tableone import TableOne
from functions.pipelineVariables import upstreamList, studyList
from functions.loadPipelineProducts import getProductFromDag, tidyOutputName
from functions.ukbb_cleaning import loadInputDataMergeDates, checkDates, factoriseData

# %% tags=["parameters"]
upstream = ["BHS Diagnostics"]
product = None

# %% define variables
def runTableOne(df, gender):
    # choose table1 reporting columns
    tableOneCols = [
        "delta_biomarker_bhs",
        "delta_bhs",
        "delta_bhs_b", 
        "BMI_factor",
        "townsend_deprivation_index.0.0",
        "qual_factor",
        "smoking_status.0.0",
        "reg_ps",
        "alcohol.0.0",
        "followupDuration",
        "incidentCad",
        "incidentCancer"]

    orderingDict = {
            "incidentCad" : [1.0,0.0], "incidentCancer":[1.0,0.0],
            "BMI_factor"  : ["<25", "25-30", "31-40", ">40"],
            "reg_ps"      : ["Yes", "No", "Unknown"],
            "qual_factor" : ["High school", "Diploma/Vocational", "Tertiary education"],
     "smoking_status.0.0" : [ 'Current', 'Previous', 'Never', 'Prefer not to answer'],
            "alcohol.0.0" : ['Daily or almost daily', 'Once or twice a week',
                             'Three or four times a week', 
                             'Ocassionally to three times a month',
                             'Never', "Unknown"]
    }
    limitingDict = {"incidentCad":1, "incidentCancer":1}
    categoricalList = [
            "incidentCad", "incidentCancer", "qual_factor",
            "smoking_status.0.0", "reg_ps", "alcohol.0.0", "BMI_factor"]

    if gender in str(["Male","Female"]):
        outputDf = TableOne(df[df["sex"]==gender], columns=tableOneCols, groupby=["age_group"],
            nonnormal=["delta_bhs", "delta_bhs_b", "delta_biomarker_bhs", "followupDuration"],
            categorical=categoricalList, order=orderingDict, limit=limitingDict)
    elif gender in "All":
        outputDf = TableOne(df, columns=tableOneCols,
            nonnormal=["delta_bhs", "delta_bhs_b", "delta_biomarker_bhs", "followupDuration"],
            categorical=categoricalList, order=orderingDict, limit=limitingDict)
    else: outputDf = None
        
    return outputDf
    
# %%
for studyType, studyName in zip(studyList, upstreamList):
    df = pd.read_parquet(getProductFromDag("Compute DASH")[studyType])
    
    # get followup date
    dates_df = pd.read_parquet("/rds/general/user/dt20/home/BHS/data/ukb_assessment_dates.parquet")
    dates_df["followupDuration"] = (dates_df["53-1.0"] - dates_df["53-0.0"]) / np.timedelta64(1, "Y")
    
    df = pd.merge(df, dates_df[["eid","followupDuration"]], how="left", on="eid")
    
    checkDates(df, studyName)
    df = factoriseData(df)
    
    genderList = ["Male", "Female", "All"]
    outputList = []
    for genderType in genderList:
        outputDf = runTableOne(df, genderType)
        if outputDf is not None:
            outputList.append(outputDf)
    
    excelOutputPath = f"output/02_eda/tables/{tidyOutputName(studyName, 'Calculate')}.xlsx"
    writer = pd.ExcelWriter(excelOutputPath, engine="openpyxl")
    for idx, outputDf in enumerate(outputList):
        outputList[idx].to_excel(writer, sheet_name=f"Sheet_{genderList[idx]}")
    writer.close()
    print(f"Saved at {excelOutputPath}")
    