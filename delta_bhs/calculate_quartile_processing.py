# store important quartiles for BHS calculations
# Date: 7 May 22
# Author: David Tang


#%%
import pandas as pd
import numpy as np

dateFields = [
    "DATE_T2",
    "DATE_T3",
    "DATE_T4",
    "DATE_T5", 
    "ATTENDANCE_DATE_T6", 
    "ATTENDANCE_DATE_D1_T7"]

bpFields = [
    "SYSBP1_T2", "SYSBP2_T2",
    "DIABP1_T2", "DIABP2_T2",
    "MEAN_SYSBP_T3", "MEAN_DIABP_T3",
    "MEAN_SYSBP_T4", "MEAN_DIABP_T4",
    "SYSBP1_T42", "SYSBP2_T42",
    "SYSBP3_T42", "SYSBP4_T42",
    "DIABP4_T42", "DIABP4_T42",
    "DIABP4_T42","DIABP4_T42",
    "MEAN_SYSBP_T5", "MEAN_DIABP_T5",
    "MEAN_SYSBP_T6", "MEAN_DIABP_T6",
    "MEAN_SYSBP_T7", "MEAN_DIABP_T7"]

censorFields = [
    "FLYTTEDATO", "DATO_EMIGRERT_EM", "DATO_DOD"]

crpFields = ["S_HS_CRP", "CRP", "S_CRP_S"]
metFields = [
    "B_HBA1C", "S_HDL", "S_LDL", "S_TRIGLYCERIDES", "S_CHOLESTEROL",
    "HBA1C", "HDL", "LDL", "TRIGLYCERIDES", "CHOLESTEROL",
    "S_GLUCOSE", "GLUCOSE", "CALCIUM", "S_CALCIUM"]

liverFields = [
    "GGT", "S_GGT", "S_ALBUMIN", "S_ALAT", "S_ASAT"]

cardioFields = ["PULSE1"]
renalFields = [
    "S_CYSTATIN_C", "CYSTATIN_C",
    "CREATININ", "CREATININ_ADJUSTED",
    "CREATININ_BLOOD", "S_CREATININ",
    "MICROALBUMINURIA_MEAN_DAY1",
    "MICROALBUMINURIA_MEAN_DAY2",
    "MICROALBUMINURIA_MEAN_DAY3",
    "MICROALBUMINURIA_DAY1",
    "MICROALBUMINURIA_DAY2",
    "MICROALBUMINURIA_DAY3",
    "U_ALBUMIN_DAY1",
    "U_ALBUMIN_DAY2",
    "U_ALBUMIN_DAY3"]

hematoFields = [
    "B_WBC", "B_THROMBOCYTE", "B_HAEMOGLOBIN",
    "WBC", "THROMBOCYTE", "HAEMOGLOBIN"]

hormonalFields = [
    "P_PTH", "S_I_PTH",
    "S_TSH", "INSULIN"]

demographicFields = [
    "AGE", "SEX"]

megaFields = []
for list in [crpFields, metFields, liverFields, cardioFields, renalFields, hematoFields, hormonalFields, demographicFields]:
    for n in [2, 3, 4, 5, 6, 7, 42, 52, 62, 72]:
        megaFields.append([x + f"_T{n}" for x in list])

df = pd.read_csv(
    "~/data/data_tromso_mar2021.csv", 
    usecols= lambda c: c in set(np.concatenate([bpFields] + [censorFields] + [dateFields] + megaFields)),
    parse_dates=dateFields + censorFields,
    dayfirst = True)

df.drop(columns=["INSULIN_T6", "INSULIN_T7"], inplace=True)

# standardise column names
df.columns = df.columns.str.replace('^.{1,2}[\_]', '')
df.rename(columns={
    "CREATININ_T42":"CREATININ_T4",
    "CREATININ_BLOOD_T5":"CREATININ_T5",
    "I_PTH_T5": "PTH_T5",
    "CRP_T52": "CRP_T5",
    "TSH_T62": "TSH_T6",
    "CRP_S_T6": "CRP_T6",
    "HS_CRP_T7": "CRP_T7",
    "INSULIN_T62": "INSULIN_T6",
    "ATTENDANCE_DATE_D1_T7":"DATE_T7",
    "ATTENDANCE_DATE_T6":"DATE_T6",
    "BP_MEDICINE_14DAYS_T3":"BP_TREATMENT_T3"},    
    inplace=True)


df["MEAN_DIABP_T2"] = (df["DIABP1_T2"] + df["DIABP2_T2"]) / 2
df["MEAN_SYSBP_T2"] = (df["SYSBP1_T2"] + df["SYSBP2_T2"]) / 2

df.to_csv("../data/t2t6biomarkers.csv", index=False)