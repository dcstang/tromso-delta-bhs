#%% 
import pandas as pd

lipid      = ["HDL", "LDL", "CHOLESTEROL", "TRIGLYCERIDES"]
metabol    = ["HBA1C", "GLUCOSE"]
cardio     = ["MEAN_SYSBP","MEAN_DIABP","PULSE1"]
inflam     = ["CRP","CALCIUM"]
renal      = ["CREATININ", "CYSTATIN_C", "U_ALBUMIN"]
hepato     = ["GGT","ALBUMIN"]
hemato     = ["WBC", "THROMBOCYTE", "HAEMOGLOBIN"]
hormone    = ["PTH", "TSH", "INSULIN"]

demograph  = ["AGE", "SEX"]
extraMarks = ["PULSE2", "PULSE3", "PHOSPHATE", "S_ALAT", "S_ASAT", "S_GGT",
    "CREATIN_KINASE", "S_CYSTATIN_C", "S_CRP_S", "FIBRINOGEN",
    "S_TSH", "URIC_ACID", "ADIPONECTIN", "PROINSULIN"]

removeList = [lipid, metabol, cardio, inflam, renal, hepato,
    hemato, hormone, demograph, extraMarks]
removeMarkersList = sum(removeList, [])
removeMarkersList = [x+"_T6" for x in removeMarkersList] + [x+"_T62" for x in removeMarkersList]

headers = pd.read_csv("~/data/data_tromso_mar2021.csv", nrows=0)
headers_T6 = [x for x in headers.columns if "_T6" in x]
headers_T6 = [x for x in headers_T6 if x not in removeMarkersList]
headers_T6 = [x for x in headers_T6 if "AGE" not in x]
headers_T6 = [x for x in headers_T6 if "URINE" not in x]

t6df = pd.read_csv(
    "~/data/data_tromso_mar2021.csv", 
    usecols=headers_T6)

t6df.drop(columns=["COMMENT_WH_T6", "ATTENDANCE_DATE_T6"], inplace=True)
t6df.to_csv("../data/t6behaviours.csv", index=False)