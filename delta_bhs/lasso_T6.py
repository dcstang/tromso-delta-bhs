#%%
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import missingno
from matplotlib.transforms import Affine2D
from matplotlib.patches import Patch

from functions.refactored_lasso import *


matplotlib.rcParams['font.family'] = ["DejaVu Sans"]


second = pd.read_csv("../data/delta_bhs/t7_second.csv")
t6df = pd.read_csv("../data/t6behaviours.csv")

outcomeDf = pd.merge(
    second,
    t6df,
    left_index =True,
    right_index = True
)

outcomeDf = outcomeDf[pd.notnull(outcomeDf["AGE_T7"])]

#%%

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


#%%
outcomeDf.dropna(axis=1, thresh=len(outcomeDf)*0.30, inplace=True)
outcomeDf.dropna(axis=0, thresh=(outcomeDf.shape[1])*0.30, inplace=True) #too strict / relax to behv only
missingno.matrix(outcomeDf)


#%%
secondaryMarkersList = ["delta_bhs", "_b", "score"] + markersList
cleanedBehavCols = outcomeDf.columns[~outcomeDf.columns.str.contains('|'.join(secondaryMarkersList))]


#%%

outputDf = lasso_stability(
    df=outcomeDf, 
    train_cols=cleanedBehavCols,
    outcome_col="delta_bhs",
    test_set_ratio=0.3,
    n_iter=100
    )

#%% plot selection stability plot

fig, ax = plt.subplots(
    figsize=(5,9.5)
)

ax.barh(outputDf["variable"].head(30), outputDf["pctSelected"].head(30))
ax.invert_yaxis()



        
#%%
calib = callibrated_lasso(outputDf, outcomeDf, "delta_bhs")

#%%
coef=calib
filterString = "aemoglobin|potassium|bilirubin|corpuscular|\
                cell|platelet|urine|calcium|testosterone|SHGB|\
                glucose|albumin|protein|phosphate|neutrophil|\
                vitamin|urate|urea|phosphatase|vitamin_D|\
                mean_sphered|cell_volume|glucose.0|T_s_r|adjusted|unadjusted".upper()

noMarkers = coef[~coef["variable"].str.contains(filterString)]

fig, ax = plt.subplots(figsize=(12,3.85*1.618))

ax.scatter(noMarkers[noMarkers["coef"]!=0]["coef"], noMarkers[noMarkers["coef"]!=0]["variable"])
ax.barh( noMarkers[noMarkers["coef"]!=0]["variable"], noMarkers[noMarkers["coef"]!=0]["coef"], color="tab:blue", height=0.1, alpha=0.5)


ax.barh( noMarkers[noMarkers["coef"]>0]["variable"], noMarkers[noMarkers["coef"]>0]["coef"], color="tab:orange", height=0.1, alpha=0.5)
ax.scatter(noMarkers[noMarkers["coef"]>0]["coef"], noMarkers[noMarkers["coef"]>0]["variable"])
ax.margins(y=0.035)

print(ax.get_yticks())
print([item.get_text() for item in ax.get_yticklabels()])
ax.set_xlabel(r"$\beta$ coefficient")
ax.set_title(r"Lasso selected coeffcients for outcome $\Delta$ BHS", fontweight="bold")