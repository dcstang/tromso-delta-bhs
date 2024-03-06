# Cox regression against delta bhs
# Aug 12 2022
# Update: Jan 17 2023 - incorporate into pipeline 
# David Tang
# 
# TODO: add regression against death
# Update: 20 Sept - rerun against incident cases and BHS score
#       : to change timeframe to age instead of time in study 
#       
#       consider 
#       40008	Age at cancer diagnosis	Cancer register  
#       40007	Age at death	Death register 
#       
#       Education level then sequentially 
#       â€¢ Behaviours (smoking, physical activity and alcohol consumption)
#         â€¢ BMI
#         â€¢ Numbers of co-morbidities and treatments
#         â€¢ BHS
#         
#         what was coefficient HR reported ? education in last paper?
#        when is administrative censoring date for this dataset? 
# Update: 22 Feb 24 - add id cluster in model

import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from lifelines import CoxPHFitter
from lifelines.exceptions import ConvergenceError
from sklearn.impute import SimpleImputer
from functions.pipelineVariables import upstreamList, studyList
from functions.loadPipelineProducts import getProductFromDag, tidyOutputName
from functions.ukbb_cleaning import factoriseData

# %% tags=["parameters"]
upstream = ["Compute DASH"]
product = None

#%% functions
def getSurvivalsList(row, timeEvent):
    if pd.isnull(row[timeEvent]):
        return [row["age.0.0"], row["age.1.0"]]
    else:
        return [row["age.0.0"], row["age.1.0"], row["age.0.0"] + row[timeEvent]/365]

def getSurvivalDf(df, columns, timeEvent, outcome):
    survivalDf = df[columns]
    
    imputerFx = SimpleImputer(strategy="most_frequent").set_output(transform="pandas")
    survivalDf = imputerFx.fit_transform(survivalDf)
    
    survivalDf.loc[:,"timepoints"] = survivalDf.apply(getSurvivalsList, timeEvent=timeEvent, axis=1)
    survivalDf.loc[:, "ageEvent"] = survivalDf["age.0.0"] + survivalDf[timeEvent]/365
    survivalDf = survivalDf.explode("timepoints")
    survivalDf[outcome] = np.where(survivalDf["timepoints"] >= survivalDf["ageEvent"], 1, 0)
    survivalDf = survivalDf.drop(columns=[timeEvent])
    
    return survivalDf

def getPrettyCoxSummary(df, duration_col, event_col, strata=None, formula=None):
    # do regression and extract exponentiated results 
    # check proportional assumptions
    df = df.astype(
            {"age.1.0": "uint32", 
             "sex": "category",
             "bhs_score.0.0" :"float64",
             "bhs_score.1.0": "float64", 
             "delta_bhs": "float64",
             "delta_biomarker_bhs": "float64",
             "age.0.0": "uint32", 
             "qual_factor": "category",
             "smoking_status.0.0": "category",
             "alcohol.0.0": "category",
             "BMI.0.0": "float64",
             "timepoints": "float64",
             "ageEvent": "float64",
             "number_medications.0.0": "uint16"})

    print(df.info())
    try:
        cph = CoxPHFitter()
        cph.fit(df, duration_col=duration_col, event_col=event_col, 
                strata=strata, cluster_col='eid', formula=formula)
        outDf = np.exp(cph.confidence_intervals_)
        outDf["coefficient"] = cph.hazard_ratios_
        outDf = outDf[["coefficient", "95% lower-bound", "95% upper-bound"]]
        outDf["note"] = pd.Series(dtype="str") # empty note

        cph.print_summary(model=f"{duration_col} - {event_col} - {formula}")  
        cph.plot()
        cph.check_assumptions(df.reset_index(), p_value_threshold=0.05, show_plots=False)
    except (np.linalg.LinAlgError, ConvergenceError) as error:
        print(f"error : {formula} - adding small penaliser")
        cph = CoxPHFitter(penalizer=0.05)
        cph.fit(df, duration_col=duration_col, event_col=event_col, 
                strata=strata, cluster_col='eid', formula=formula)
        outDf = np.exp(cph.confidence_intervals_)
        outDf["coefficient"] = cph.hazard_ratios_
        outDf = outDf[["coefficient", "95% lower-bound", "95% upper-bound"]]
        outDf["note"] = "*" # note that penalisation applied

        cph.print_summary(model=f"{duration_col} - {event_col} - {formula}")  
        cph.plot()
        cph.check_assumptions(df.reset_index(), p_value_threshold=0.05, show_plots=False)
    except Exception as error:
        print(f"error : {formula} - skipping")
        outDf = pd.DataFrame(columns=["coefficient", "95% lower-bound", 
                                      "95% upper-bound", "note"])
    
    return outDf

def getOnlyScoreHazardRatios(prettyCoxDf, bhsType, outcomeType, strataType, adjustmentType):
    # get solely the score HR for joining into final output
    outDf = prettyCoxDf[prettyCoxDf.index == bhsType]
    outDf.insert(0, "outcome_type", outcomeType)
    outDf.insert(1, "strata", strataType)
    outDf.insert(2, "adjustment", adjustmentType)    
    
    return outDf

def calculateHazardOutcome(inputDf, timeOutcomeCol, outcomeCol, savefileName, outcomeType):
    # main function with sex stratification
    columnsNeeded = ["eid", "age.1.0", "sex",
                    "bhs_score.0.0", "bhs_score.1.0", "delta_bhs",
                    "delta_biomarker_bhs"]
    varList = ["age.0.0", "qual_factor",
            "smoking_status.0.0", "alcohol.0.0", "BMI.0.0",
            "number_medications.0.0"]
    outcomeDf = getSurvivalDf(inputDf, columnsNeeded + [timeOutcomeCol, outcomeCol] + varList,
                    timeOutcomeCol, outcomeCol)
    
    maleOutcomeDf = outcomeDf[outcomeDf["sex"]=="Male"]
    femaleOutcomeDf = outcomeDf[outcomeDf["sex"]=="Female"]

    resultList = []
    
    adjustmentLabelList = ["Age", "Education", "Smoking", "Alcohol", "BMI", "Medications"]

    # stratify and nested loop for all variables
    for stratifiedData, strataType in zip([maleOutcomeDf, femaleOutcomeDf, outcomeDf], ["Male", "Female", "All"]):
        for bhsType in ["delta_bhs", "delta_biomarker_bhs"]:
            for varLength in range(0, 7):
                
                # to pass sex into output df
                modelStrataType=None
                if strataType == "All":
                    modelStrataType=["sex"]
                    
                _tempDf = getOnlyScoreHazardRatios(getPrettyCoxSummary(
                    stratifiedData, duration_col="timepoints", 
                    event_col=outcomeCol, strata=modelStrataType,
                    formula=" + ".join([bhsType] + varList[0:varLength])),
                    bhsType=bhsType,  
                    outcomeType=outcomeCol, 
                    strataType=strataType,
                    adjustmentType=" + ".join(adjustmentLabelList[0:varLength]))
                
                resultList.append(_tempDf)

    savefileName = tidyOutputName(savefileName, "Calculate")
    savePath = f"output/05_outcome/hazard_tables/{savefileName}_{outcomeType.lower()}.xlsx"        
    pd.concat(resultList).to_excel(savePath)

#%% main
def getHazardTables(inputDf, studyName):
    for outcomeType in ["Cancer", "Cad", "CVD"]:
        calculateHazardOutcome(inputDf=inputDf, 
                               timeOutcomeCol=f"ttd{outcomeType}", 
                               outcomeCol=f"case{outcomeType}",
                               savefileName=studyName,
                               outcomeType=outcomeType)

for studyType, studyName in zip(studyList, upstreamList):
    df = pd.read_parquet(getProductFromDag("Compute DASH")[studyType])
    df = factoriseData(df)
    getHazardTables(df, studyName)
