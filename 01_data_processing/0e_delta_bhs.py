# """
# Delta BHS / Delta Biomarker BHS calculation
# Here we are using a complete cases version 
# 0.7-17% missingness for biomarkers 
# to parameterise and factorise code
# """

import pandas as pd
import numpy as np
from functions.bhs_calc_functions import getAgeGroupList, getAgeThresholds, \
                                    checkListClean, biomarkerScore, count_scores
from sklearn.impute import KNNImputer
from sklearn.preprocessing import MinMaxScaler
from functions.pca_bhs import *

# %% tags=["parameters"]
upstream = ['Pull dietary variables']
product = None
biomarker_lower_quartile_scored = None
complete_cases = None
knn_impute = None
continuous_pca_biomarker = None
continuous_pca_subsystem = None
continuous_pca_subsystem_scaled = None

#%% data preparation
df = pd.read_parquet(upstream['Pull dietary variables']['data'])

# get dates for checking if came for followup & for cox regression later 
assessmentDatesDf = pd.read_parquet("data/ukb_assessment_dates.parquet")

df = pd.merge(
    df,
    assessmentDatesDf,
    how="left",
    on="eid")

df = df.rename(columns={"genetic_sex.0.0":"sex"})

markersList = ["glycated_haemoglobin","HDL_cholesterol","LDL_direct","triglycerides","systolic_bp","diastolic_bp",
 "pulse_rate","c.reactive_protein","IGF1","creatinine", "cystatin_C", "alanine_aminotransferase",
 "aspartate_aminotransferase","gamma_glutamyltransferase"]

biomarkersColumns = df.columns[
    df.columns.str.contains('|'.join([x+".0.0" for x in markersList]))|
    df.columns.str.contains('|'.join([x+".1.0" for x in markersList]))
].append(pd.Index(["eid", "age.0.0", "age.1.0", "sex"]))

prevalentDisease = df[
    (df["prevalentCancer"]==1)|
    (df["prevalentCad"]==1)|
    (df["prevalentCVD"]==1)]["eid"]

# population selection
biomarkersDf = df[~(df["eid"].isin(prevalentDisease)) &
                  (pd.notnull(df["53-1.0"])) & 
                  (pd.notnull(df["sex"]))]
biomarkersDf = biomarkersDf[biomarkersColumns]

if complete_cases is True:
    biomarkersDf = biomarkersDf.dropna()

if knn_impute is True:
    knn = KNNImputer().set_output(transform="pandas")
    for ageGroup in getAgeGroupList(biomarkersDf, "age.0.0"):
        biomarkersDf.loc[ageGroup,
                          biomarkersDf.columns.str.contains('|'.join([x+".0.0" for x in markersList]))]=\
        knn.fit_transform(biomarkersDf.loc[ageGroup,
                          biomarkersDf.columns.str.contains('|'.join([x+".0.0" for x in markersList]))])
    
    knn = KNNImputer().set_output(transform="pandas")
    for ageGroup in getAgeGroupList(biomarkersDf, "age.1.0"):
        biomarkersDf.loc[ageGroup,
                          biomarkersDf.columns.str.contains('|'.join([x+".1.0" for x in markersList]))]=\
        knn.fit_transform(biomarkersDf.loc[ageGroup,
                          biomarkersDf.columns.str.contains('|'.join([x+".1.0" for x in markersList]))])
    

# print population selection change                          
print(df.shape)
print(biomarkersDf.shape)
print(f"Unknown sex, n= {((pd.notnull(df['53-1.0'])) & (pd.isnull(df['sex']))).sum()}")
print(f"Prevalent cancer, n= {((pd.notnull(df['53-1.0'])) & (df['prevalentCancer']==1)).sum()}")
print(f"Prevalent cad, n= {((pd.notnull(df['53-1.0'])) & (df['prevalentCad']==1)).sum()}")
print(f"Prevalent cvd, n= {((pd.notnull(df['53-1.0'])) & (df['prevalentCVD']==1)).sum()}")
print(f"Total excluded due to prevalent disease: {len(prevalentDisease)}")

# %% 
# ORIGINAL BHS LIST
metabol    = ["glycated_haemoglobin","HDL_cholesterol","LDL_direct","triglycerides"]
cardio     = ["systolic_bp","diastolic_bp","pulse_rate"]
inflam     = ["c.reactive_protein","IGF1"]
renal      = ["creatinine", "cystatin_C"]
hepato     = ["alanine_aminotransferase","aspartate_aminotransferase","gamma_glutamyltransferase"]

baseline = biomarkersDf[biomarkersDf.columns[
    biomarkersDf.columns.str.contains('|'.join([x+".0.0" for x in markersList]))].append(pd.Index(["sex", "eid"]))]
second = biomarkersDf[biomarkersDf.columns[
    biomarkersDf.columns.str.contains('|'.join([x+".1.0" for x in markersList]))].append(pd.Index(["sex", "eid"]))]

pd.options.mode.chained_assignment = None
baseline["age"] = df["age.0.0"]
second["age"] = df["age.1.0"]


# %%
##### calculate bhs score ######
conditions = [
    baseline["age"] < 50,
    (baseline["age"] >= 50) & (baseline["age"] <= 64),
   baseline["age"] > 64]

conditionsSecond = [
    second["age"] < 50,
    (second["age"] >= 50) & (second["age"] <= 64),
    second["age"] > 64]

choices = ["<50","50-64", ">64"]
baseline["age_group"] = np.select(conditions, choices)
second["age_group"] = np.select(conditions, choices)

originalColList = baseline.columns.drop(["age", "eid", "sex", "HDL_cholesterol.0.0"])
originalColListSecond = second.columns.drop(["age", "eid", "sex", "HDL_cholesterol.1.0"])

baseline, second = biomarkerScore(
                        baseline, second, 
                        originalColList, originalColListSecond,
                        biomarker_lower_quartile_scored=biomarker_lower_quartile_scored,
                        reverse=False)
baseline, second = biomarkerScore(
                        baseline, second, 
                        ["HDL_cholesterol.0.0"],  ["HDL_cholesterol.1.0"],
                        biomarker_lower_quartile_scored=biomarker_lower_quartile_scored,
                        reverse=True)

# BHS subsystem calculation
systemNameList = ["metabol", "cardio", "inflam", "renal", "hepato"]

for idx, subsystem in enumerate([metabol, cardio, inflam, renal, hepato]):
    baseline[f"{systemNameList[idx]}_score"] = baseline[[x+"_score" for x in subsystem]].sum(axis=1)/len(subsystem)
    second[f"{systemNameList[idx]}_score"] = second[[x+"_score" for x in subsystem]].sum(axis=1)/len(subsystem)
    second[f"{systemNameList[idx]}_score_b"] = second[[x+"_score_b" for x in subsystem]].sum(axis=1)/len(subsystem)

# full BHS score calculation
baseline["bhs_score"] = baseline[[x+"_score" for x in systemNameList]].sum(axis=1)/len(systemNameList)
second["bhs_score"]   = second[[x+"_score" for x in systemNameList]].sum(axis=1)/len(systemNameList)
second["bhs_score_b"] = second[[x+"_score_b" for x in systemNameList]].sum(axis=1)/len(systemNameList)


#%%
###### calculate delta biomarker 'bhs' ######
# 1. calculate biomarker difference T2 - T1
# 2. get quartile cutoffs on difference T2-T1
# 3. calculate subsystem score
# ie. biomarker_cardio_score
# 4. then calculate whole bhs 

# reset age grouping to baseline for biomarkers bhs      
second["age"] = df["age.0.0"]

# delta_biomarker_"marker"
for idx, subsystem in enumerate([metabol, cardio, inflam, renal, hepato]):
    for marker in subsystem:
        second[f"delta_biomarker_{marker}"] = second[f"{marker}.1.0"] - baseline[f"{marker}.0.0"]

deltaColumns = second.columns[second.columns.str.contains("delta_biomarker_")]

# delta_cholesterol:
# need to change the hdl to score for largest decrease over time
# if t2 - t1 = delta regular, then t2 - t1 * -1 flips this 
second["delta_biomarker_HDL_cholesterol"] = second["delta_biomarker_HDL_cholesterol"] * -1

### delta biomarker options section ###
# delta_biomarker_"marker"_score; age/sex group specific
# lower quartile scoring option 
# initial continuous delta biomarker pca version with 5 components 
      
if biomarker_lower_quartile_scored is False:
    for ageGroup in getAgeGroupList(second):
        for col in deltaColumns:
            second.loc[ageGroup,f"{col}_score"] = np.select(
                [second.loc[ageGroup,col] > second[ageGroup][col].quantile([0.75]).values[0],
                    second.loc[ageGroup,col] <= second[ageGroup][col].quantile([0.75]).values[0]],
                [1.0, 0.0],
                default=np.nan)  

if biomarker_lower_quartile_scored is True:
    for ageGroup in getAgeGroupList(second):
        for col in deltaColumns:
            second.loc[ageGroup,f"{col}_score"] = np.select(
                [second.loc[ageGroup,col] > second[ageGroup][col].quantile([0.75]).values[0],
                 second.loc[ageGroup,col] < second[ageGroup][col].quantile([0.25]).values[0],
                 (second.loc[ageGroup,col] <= second[ageGroup][col].quantile([0.75]).values[0]) &
                 (second.loc[ageGroup,col] >= second[ageGroup][col].quantile([0.25]).values[0])],
                [1.0, -1.0, 0.0],
                default=np.nan)  

## here do whole pca and score plots 
# after done the next section will take mean of all 5 pcs 
# function needs to take in age gorups and work on loc pandas 
      # a) pca_biomarker : 5 PCs of all 14 biomarkers
      # b) pca_subsystem : 1 PC for each subsystem
      # c) pca_subsystem_scaled : 1 PC for each subsystem, overall score rescaled to 0-1
if continuous_pca_biomarker is True:
  pcaStudyName = f"05_pca_bhs_knn_{knn_impute}_complete_cases_{complete_cases}"
  second = pcaBiomarkerScore(second, deltaColumns, systemNameList, pcaStudyName)

if continuous_pca_subsystem is True:
  second, explainedVarDf = getPcaBhsSubsystem(second, systemNameList,
                                             metabol, cardio, inflam, renal, hepato)
  pcaStudyName = f"05_pca_subsystem_bhs_knn_{knn_impute}_complete_cases_{complete_cases}"
  explainedVarDf.to_csv(f"output/01_data_processing/pca_subsystem_diagnostics/{pcaStudyName}.csv", index=False)
      
# biomarker BHS subsystem calculation, ie. delta_biomarker_"subsystem"_score
# only if continuous pca is not done 
if continuous_pca_biomarker is False and continuous_pca_subsystem is False:
    for idx, subsystem in enumerate([metabol, cardio, inflam, renal, hepato]):
        second[f"delta_biomarker_{systemNameList[idx]}_score"] = second[["delta_biomarker_"+x+"_score" for x in subsystem]].sum(axis=1)/len(subsystem)

# biomarker whole delta_biomarker_bhs calculation 
second["delta_biomarker_bhs"]   = second[["delta_biomarker_"+x+"_score" for x in systemNameList]].sum(axis=1)/len(systemNameList)
second["delta_bhs"]   = second["bhs_score"] - baseline["bhs_score"]
second["delta_bhs_b"] = second["bhs_score_b"] - baseline["bhs_score"] # nina's bhs

if continuous_pca_subsystem_scaled is True:
    scaler = MinMaxScaler(feature_range=(-1, 1))
    second["delta_biomarker_bhs"] = scaler.fit_transform(second[["delta_biomarker_bhs"]])

# %%
# subsystem contribution to delta BHS scores

def getDotMatrix(df, score_suffix, score_prefix=""):
    t1 = df[[score_prefix+x+score_suffix for x in systemNameList]]
    t1 = t1.eq(t1.max(axis=1), axis=0) # equals to max
    t1 = t1.dot(t1.columns + " ") # dot matrix multiplication 
    outputSeries = t1.apply(count_scores)
    return outputSeries

second.loc[:,"delta_subsystem_contrib"]           = getDotMatrix(second, "_score")
second.loc[:,"delta_biomarker_subsystem_contrib"] = getDotMatrix(second, "_score", "delta_biomarker_")
second.loc[:,"delta_subsystem_contrib_b"]         = getDotMatrix(second, "_score_b")

# rename scores to .0.0 for baseline 
baseline = baseline.rename(columns=dict(zip(
    baseline.columns[baseline.columns.str.contains("score")],
    [x+'.0.0' for x in baseline.columns[baseline.columns.str.contains("score")]])))

second = second.rename(columns=dict(zip(
    second.columns[second.columns.str.contains("score")],
    [x+'.1.0' for x in second.columns[second.columns.str.contains("score")]])))


# %% saving
outputDf = pd.merge(
    df,
    baseline[baseline.columns[baseline.columns.str.contains("score")].tolist() + ["eid"]],
    how="right",
    left_on="eid",
    right_on="eid"
)

outputDf = pd.merge(
    outputDf,
    second[second.columns[second.columns.str.contains("score")].tolist() + \
           second.columns[second.columns.str.contains("contrib")].tolist() + \
           ["eid", "delta_bhs", "delta_bhs_b", "delta_biomarker_bhs"]],
    how="right",
    left_on="eid",
    right_on="eid"
)

outputDf.to_parquet(product["data"])

# %% diagnostics
outputDf.shape

#%% save thresholds for analysing
outputPath = "output/01_data_processing/quartiles/"
outputPathExcel = "output/01_data_processing/quartiles/excel/"

baselineOutputPath = f"{outputPath}baseline_quartiles_complete_cases{complete_cases}_impute{knn_impute}_pca{continuous_pca_biomarker}"
getAgeThresholds(baseline, [x+".0.0" for x in markersList]).to_html(f"{baselineOutputPath}.html")
getAgeThresholds(baseline, [x+".0.0" for x in markersList]).to_excel(f"{baselineOutputPath}.xlsx")
                                                                     
secondOutputPath = f"{outputPath}second_quartiles_complete_cases{complete_cases}_impute{knn_impute}_pca{continuous_pca_biomarker}"
getAgeThresholds(second, [x+".1.0" for x in markersList]).to_html(f"{secondOutputPath}.html")
getAgeThresholds(second, [x+".1.0" for x in markersList]).to_excel(f"{secondOutputPath}.xlsx")