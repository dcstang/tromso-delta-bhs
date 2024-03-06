import numpy as np
import pandas as pd

def relabelNames(df, relabelDict):
    
    df["variable"] = df["variable"].str.replace(".0.0", "", regex=False)
    df = pd.merge(
        df,
        relabelDict[["CodingName", "FigureName"]],
        how="left",
        left_on="variable",
        right_on="CodingName"
    )
    
    df.loc[df["variable"]=="meanNOx", "FigureName"] = "Mean NOx Concentration (2006-2010)"
    df.loc[df["variable"]=="sex", "FigureName"] = "Sex"
    
    df.loc[
        pd.isnull(df["FigureName"]), "FigureName"] = df.loc[
                            pd.isnull(df["FigureName"]), "variable"].str.replace("_", " ")
    
    return df

def getCategory(df, relabelDict):
    
    df["variable"] = df["variable"].str.replace(".0.0", "", regex=False)
    df = pd.merge(
        df,
        relabelDict[["CodingName", "Category"]],
        how="left",
        on="CodingName"
    )
    
    return df

def cleanMergeCat(df, recoding_dict):
    df["variable"] = df["Unnamed: 0"].str.replace(".0.0_[^_]+$", "", regex=True)
    df = relabelNames(df, recoding_dict)
    df = getCategory(df, recoding_dict)
    return df

def filterBiomarkersOut(df):
    biomarkerList = ["potassium","sodium","cell","neutrophil","platelet","urine",
                        "bilirubin","phosphatase", "Haemoglobin", "testosterone",
                        "SHGB", "glucose", "urate", "rbc", "albumin", "phosphate",
                        "calcium", "vitamin", "eosinophil", "lymphocyte", "monocyte",
                        "T_S_r", "total_protein"]
    df = df[~df["variable"].str.contains("|".join(biomarkerList))]
    return df

def loadInputDataMergeDates(inputDataPath, ukb_dates):
    df = pd.read_parquet(inputDataPath)
    ukbDateSubset = ukb_dates[ukb_dates["eid"].isin(df["eid"])].copy()
    ukbDateSubset.loc[:,"followupDuration"] = (ukbDateSubset["53-1.0"] - ukbDateSubset["53-0.0"]).dt.days
    ukbDateSubset = ukbDateSubset.reset_index()
    df = pd.merge(df, ukbDateSubset[["followupDuration", "eid"]], how="left", on="eid")
    df["followupDuration"] = df["followupDuration"].div(365).round(2)
    return df 


def checkDates(df, dfTypeTitle):
    """
    check dates makes sense
    # ie. death after diagnosis and recruitment 
    """
    print(dfTypeTitle)
    for outcomeDeath in ["dateDeathCancer", "dateDeathCad"]:
        for checkDate in ["date_recr", "dateDiagnosisCancer", "dateDiagnosisCad"]:
            print(f"Check {outcomeDeath} > {checkDate}: {df[df[checkDate] > df[outcomeDeath]].empty}")

def factoriseData(df):
    # Clean up groupings for presentable table 1
    # also for use in the cox models - categorical variables
    df["BMI_factor"] = np.select(
        [df["BMI.0.0"] < 25,
        (df["BMI.0.0"] >= 25) & (df["BMI.0.0"] < 30),
        (df["BMI.0.0"] >= 30) & (df["BMI.0.0"] < 40),
        df["BMI.0.0"] >= 40],
        ["<25", "25-30", "31-40", ">40"],
        default=np.nan)

    df["reg_ps"] = np.select(
        [df["regular_prescription_meds.0.0"] == "Prefer not to answer",
        df["regular_prescription_meds.0.0"] == "Do not know",
        df["regular_prescription_meds.0.0"] == "No",
        df["regular_prescription_meds.0.0"] == "Yes - you will be asked about this later by an interviewer"],
        ["Unknown", "Unknown", "No", "Yes"],
        default="Unknown")

    df["qual_factor"] = np.select(
        [df["qualifications.0.0"] == "NVQ or HND or HNC or equivalent",
        df["qualifications.0.0"] == "Other professional qualifications eg: nursing, teaching",
        df["qualifications.0.0"] == "CSEs or equivalent",
        df["qualifications.0.0"] == "A levels/AS levels or equivalent",
        df["qualifications.0.0"] == "O levels/GCSEs or equivalent",
        df["qualifications.0.0"] == "College or University degree"],
        ["Diploma/Vocational", "Diploma/Vocational", "High school", "High school",
         "High school", "Tertiary education"],
        default="Unknown")  

    df["alcohol.0.0"] = np.where(
        df["alcohol.0.0"] == "Special occasions only",
        "One to three times a month",
        df["alcohol.0.0"])

    df["alcohol.0.0"] = np.where(
        df["alcohol.0.0"] == "Prefer not to answer",
        "Unknown",
        df["alcohol.0.0"])

    df["alcohol.0.0"] = np.where(
        df["alcohol.0.0"] == "One to three times a month",
        "Ocassionally to three times a month",
        df["alcohol.0.0"])

    df["smoking_status.0.0"] = np.where(
        pd.isnull(df["smoking_status.0.0"]),
        "Prefer not to answer",
        df["smoking_status.0.0"])

    df["age_group"] = np.select(
            [(df["age.0.0"] < 50),  
            (df["age.0.0"] >= 50) & (df["age.0.0"] <= 64), 
            (df["age.0.0"] > 64)],
            ["<50", "50-64", ">64"],
            default=np.nan)

    return df
