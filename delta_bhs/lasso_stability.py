#%%
import pandas as pd
import sys
sys.path.append('~/scripts/tromso-delta-bhs')
sys.path.append('../')
from functions.refactored_lasso import *


second = pd.read_csv("../data/delta_bhs/t7_second.csv")
t6df = pd.read_csv("../data/t6behaviours.csv")

outcomeDf = pd.merge(
    second,
    t6df,
    left_index =True,
    right_index = True
)

outcomeDf = outcomeDf[pd.notnull(outcomeDf["AGE_T7"])]


lipid      = ["HDL", "LDL", "CHOLESTEROL", "TRIGLYCERIDES"]
metabol    = ["HBA1C", "GLUCOSE"]
cardio     = ["MEAN_SYSBP","MEAN_DIABP","PULSE1"]
inflam     = ["CRP","CALCIUM"]
renal      = ["CREATININ", "CYSTATIN_C", "U_ALBUMIN"]
hepato     = ["GGT","ALBUMIN"]
hemato     = ["WBC", "THROMBOCYTE", "HAEMOGLOBIN"]
hormone    = ["PTH", "TSH", "INSULIN"]
misc       = ["DATE", "cardio|metabol|renal|hepato|hemato|lipid|hormone"]

markersList = lipid + metabol + cardio + inflam + renal + hemato + hormone + misc

behaviourCols = outcomeDf.columns[~outcomeDf.columns.str.contains('|'.join(markersList))]
print(len(behaviourCols))


outcomeDf.dropna(axis=1, thresh=len(outcomeDf)*0.30, inplace=True)
outcomeDf.dropna(axis=0, thresh=(outcomeDf.shape[1])*0.30, inplace=True) #too strict / relax to behv only
secondaryMarkersList = ["delta_bhs", "_b", "score"] + markersList
cleanedBehavCols = outcomeDf.columns[~outcomeDf.columns.str.contains('|'.join(secondaryMarkersList))]



outputDf = lasso_stability(
    df=outcomeDf, 
    train_cols=cleanedBehavCols,
    outcome_col="delta_bhs",
    test_set_ratio=0.3,
    n_iter=100
    )

outputDf.to_csv("../data/delta_bhs/t7_stability_100.csv", index=False)
