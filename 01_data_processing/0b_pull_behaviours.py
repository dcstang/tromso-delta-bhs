"""
combining behaviours and additional measures into behaviourDf
# we are focusing on exposome so dropping all other biomarkers 

5 Jan 2023: parameterise pipeline 
"""

import pandas as pd

# %% tags=["parameters"]
upstream = ['Merge UKBB raw with outcomes']
product = None

#%% 
additionalDf = pd.read_parquet("data/ukb_additional.parquet")
df = pd.read_parquet(upstream['Merge UKBB raw with outcomes']['data'])

additionalDf["eid"] = additionalDf["eid"].astype(int)
print(f"UKBB shape: {df.shape} /n AdditionalBehav Df shape: {additionalDf.shape}")

#%% setup exclusion columns
additionalDf.columns

markersList = ["glycated_haemoglobin","HDL_cholesterol","LDL_direct","triglycerides","systolic_bp","diastolic_bp",
     "pulse_rate","c.reactive_protein","IGF1","creatinine", "cystatin_C", "alanine_aminotransferase",
     "aspartate_aminotransferase","gamma_glutamyltransferase","cholesterol","Cholesterol","lipids","Lipids",
     "triglycerides", "Triglycerides", "Esters", 
     "haemoglobin", "platlet", "Albumin", "Acetate",
     "reticulocyte", "leukocyte", "basophil", "erythrocyte", "_NG",
     "VLDL", "HDL", "LDL", "lipoprotein", "Acid"] + \
    ["age", "FVC", "PEF", "FEV"] + ["score", "bhs", "delta"] + ['stillbirths']

otherBiomarkersList = ["potassium","sodium","cell","neutrophil","platelet","urine",
                        "bilirubin","phosphatase", "Haemoglobin", "testosterone",
                        "SHGB", "glucose", "urate", "rbc", "albumin", "phosphate",
                        "calcium", "vitamin", "eosinophil", "lymphocyte", "monocyte",
                        "T_S_r", "total_protein", "urea", "corpuscular"]

columnsForExclusion = markersList + otherBiomarkersList

#%% getting additional behaviours ready
def getRecruitmentColumns(df, exclusionList):
    behaviourCols = df.columns[~df.columns.str.contains('|'.join(markersList + otherBiomarkersList))]

    # get only recruitment behaviours
    originalMeasure = []
    for behaviour in behaviourCols:
        if ".0.0" in behaviour:
            originalMeasure.append(behaviour)

    print(len(originalMeasure))
    
    return originalMeasure

len(df.columns[~df.columns.str.contains('|'.join(markersList + otherBiomarkersList))])


df["genetic_ethnic_grouping.0.0"] = df["genetic_ethnic_grouping.0.0"].fillna(value="Other")
additionalRecruitmentBehaviourCols = getRecruitmentColumns(additionalDf, columnsForExclusion)

#%% saving output

df.drop(columns=["ethnicity.0.0", "smoking_status.0.0"], inplace=True)
df = pd.merge(
    df, additionalDf[additionalRecruitmentBehaviourCols + ["eid"]],
    how="left",
    left_on="eid", right_on="eid"
)

df.to_parquet(product['data'])

