# calculate BHS score for TROMSO
#%%

import pandas as pd
import numpy as np
import progressbar
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("../data/t2t6biomarkers.csv",
    parse_dates=["DATE_T5", "DATE_T6", "DATE_T7"])

# UPDATED BHS LIST
lipid      = ["HDL", "LDL", "CHOLESTEROL", "TRIGLYCERIDES"]
metabol    = ["HBA1C", "GLUCOSE"]
cardio     = ["MEAN_SYSBP","MEAN_DIABP","PULSE1"]
inflam     = ["CRP","CALCIUM"]
renal      = ["CREATININ", "CYSTATIN_C", "U_ALBUMIN"]
hepato     = ["GGT","ALBUMIN"]
hemato     = ["WBC", "THROMBOCYTE", "HAEMOGLOBIN"]
hormone    = ["PTH", "TSH", "INSULIN"]

bhsList = [lipid, metabol, cardio, inflam, renal, hepato, hemato, hormone]


# refurnishing age groups for T6
df["t6delta"] = (df["DATE_T6"] - df["DATE_T5"]).dt.days/365
df["t6delta_back"] = (df["DATE_T7"] - df["DATE_T6"]).dt.days/365

# check how many in T6, and how many with age 
# 4k with t6 delta out of 10k

df["AGE_T6"] = df["AGE_T5"] + df["t6delta"] 
ageGroupT6 = pd.read_csv(
    "~/data/data_tromso_mar2021.csv", 
    usecols=["AGE_GROUP10_T6"])

with progressbar.ProgressBar(max_value=len(df["PULSE1_T6"].index)) as bar:
    i = 0
    for idx in df["PULSE1_T6"].index:
        if pd.isnull(df.loc[idx, "AGE_T6"]):
            if pd.notnull(df.loc[idx, "AGE_T5"]):
                df.loc[idx, "AGE_T6"] = df.loc[idx, "AGE_T5"] + df["t6delta"].mean()
            elif pd.notnull(df.loc[idx, "AGE_T7"]):
                df.loc[idx, "AGE_T6"] = df.loc[idx, "AGE_T7"] - df.loc[idx, "t6delta_back"]
            else:
                df.loc[idx, "AGE_T6"] = ageGroupT6.loc[idx, "AGE_GROUP10_T6"]
        i += 1
        bar.update(i)


#%%
baseline = df[df.columns[df.columns.str.contains("T6")]]
second = df[df.columns[df.columns.str.contains("T7")]]

second["age"] = df["AGE_T7"]
baseline["age"] = df["AGE_T6"]

baseline = baseline.loc[:, ~baseline.columns.duplicated()]
second = second.loc[:, ~second.columns.duplicated()]

originalColList = baseline.columns.to_list()
originalColListSecond = second.columns.to_list()    
originalColList.remove("DATE_T6")
originalColListSecond.remove("DATE_T7")

# calculate bhs score per marker
def getAgeGroupList(df):
    return([df["age"] < 50, (df["age"] >= 50) & (df["age"] < 64), df["age"] >= 64])

pd.options.mode.chained_assignment = None
    
conditions = [
    baseline["age"] < 50,
    (baseline["age"] >= 50) & (baseline["age"] < 64),
    baseline["age"] >= 64,
]

conditionsSecond = [
    baseline["age"] < 50,
    (baseline["age"] >= 50) & (baseline["age"] < 64),
    baseline["age"] >= 64,
]

choices = ["<50","50-64", ">64"]
baseline["age_group"] = np.select(conditions, choices)
second["age_group"] = np.select(conditionsSecond, choices)

# age group specific quartiles
for ageGroup in getAgeGroupList(baseline):
    for col in originalColList:
        baseline.loc[ageGroup,f"{col[:-3]}_score"] = np.where(
        baseline.loc[ageGroup,col] > baseline[ageGroup][col].quantile([0.75]).values[0],
        1.0, 0.0)
        
for ageGroup in getAgeGroupList(second):
    for col in originalColListSecond:
        second.loc[ageGroup,f"{col[:-3]}_score"] = np.where(
        second.loc[ageGroup,col] > second[ageGroup][col].quantile([0.75]).values[0],
        1.0, 0.0)       
        
for ageGroup in getAgeGroupList(second):
    for col, baseCol in zip(originalColListSecond, originalColList):
        second.loc[ageGroup,f"{col[:-3]}_score_b"] = np.where(
        second.loc[ageGroup,col] > baseline[ageGroup][baseCol].quantile([0.75]).values[0],
        1.0, 0.0)    

# BHS subsystem calculation
systemNameList = ["lipid", "metabol", "cardio", "inflam", "renal", "hepato", "hepato", "hemato", "hormone"]

def returnMarkerScore(df, idx, subsystem):
    df[f"{systemNameList[idx]}_score"] = df.loc[:,df.columns.isin([x+"_score" for x in subsystem])].sum(axis=1) /\
        df.loc[:,df.columns.isin([x+"_score" for x in subsystem])].shape[1]

def returnMarkerScore_b(df, idx, subsystem):
    df[f"{systemNameList[idx]}_score_b"] = df.loc[:,df.columns.isin([x+"_score_b" for x in subsystem])].sum(axis=1) /\
        df.loc[:,df.columns.isin([x+"_score_b" for x in subsystem])].shape[1]

for idx, subsystem in enumerate(bhsList):
    returnMarkerScore(baseline, idx, subsystem)
    returnMarkerScore(second, idx, subsystem)
    returnMarkerScore_b(second, idx, subsystem)

# full BHS score calculation
systemNameList = ["lipid", "metabol", "cardio", "inflam", "renal", "hepato", "hepato", "hemato"]
baseline["bhs_score"] = baseline[[x+"_score" for x in systemNameList]].sum(axis=1)/len(systemNameList)
second["bhs_score"]   = second[[x+"_score" for x in systemNameList]].sum(axis=1)/len(systemNameList)
second["bhs_score_b"]   = second[[x+"_score_b" for x in systemNameList]].sum(axis=1)/len(systemNameList)

second["delta_bhs"] = second["bhs_score"] - baseline["bhs_score"]
second["delta_bhs_b"] = second["bhs_score_b"] - baseline["bhs_score"]



#%% boxplots for subsystem scores and bhs scores
fig, ax = plt.subplots(
    ncols=3,
    figsize=(23,5),
    sharey=True,
    gridspec_kw={"wspace":0}
)

boxplotDf = pd.concat(
    [baseline.loc[pd.notnull(baseline["age"]), [x + "_score" for x in systemNameList] + ["age"] +["bhs_score"]]
    .melt(id_vars="age", var_name="subsystem")
    .assign(time="baseline"),
    second.loc[pd.notnull(second["age"]), [x + "_score" for x in systemNameList] + ["age"] +["bhs_score"] + ["delta_bhs"] + ["delta_bhs_b"]]
    .melt(id_vars="age", var_name="subsystem")
    .assign(time="followup")],
    axis=0
)

for idx, ageGroup in enumerate(getAgeGroupList(boxplotDf)):
    sns.boxplot(x="subsystem", y="value", hue="time", data=boxplotDf[ageGroup], ax=ax[idx])

for idx, ageGroup in enumerate(["<50 years", "50-64 years", ">64 years"]):
    ax[idx].set_title(ageGroup)   
    ax[idx].set_xlabel("")
    ax[idx].get_legend().remove()
    ax[idx].tick_params(axis="x", rotation=45)
    
    if idx > 0:
        ax[idx].set_ylabel("")
        ax[idx].axes.yaxis.set_visible(False)
        
ax[1].legend(loc="lower center", bbox_to_anchor=(0.5, 0.1))
plt.savefig("../figures/delta_bhs/bhs_scores.png", bbox_inches="tight")

#%%
baseline.to_csv("../data/delta_bhs/t6_baseline.csv", index=False)
second.to_csv("../data/delta_bhs/t7_second.csv", index=False)