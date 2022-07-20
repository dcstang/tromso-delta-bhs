# Show sub-system scores for BHS
# Date: 9 May 22
# Author: David Tang

#%%
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
import progressbar
import statsmodels.formula.api as smf
from sklearn.preprocessing import minmax_scale, StandardScaler, scale

"""
Systems to look at : 

1. Liver
2. Renal
3. Cardiac
4. Haematological
5. Metabolic
6. Inflammatory
7. Hormonal 
"""



#%% UPDATED BHS LIST
lipid      = ["HDL", "LDL", "CHOLESTEROL", "TRIGLYCERIDES"]
metabol    = ["HBA1C", "GLUCOSE"]
cardio     = ["MEAN_SYSBP","MEAN_DIABP","PULSE1"]
inflam     = ["CRP","CALCIUM"]
renal      = ["CREATININ", "CYSTATIN_C", "U_ALBUMIN"]
hepato     = ["GGT","ALBUMIN","ALAT", "ASAT"]
hemato     = ["WBC", "THROMBOCYTE", "HAEMOGLOBIN"]
hormone    = ["PTH", "TSH", "INSULIN"]

bhsList = [lipid, metabol, cardio, inflam, renal, hepato, hemato, hormone]
#%% plot all systems distribution

fig, ax = plt.subplots(
    nrows=4, ncols=8,
    figsize=(21,3.5*4),
    gridspec_kw={"wspace":0.35}
)

for i in fig.axes:
    i.set_axis_off()

with progressbar.ProgressBar(max_value=np.concatenate(bhsList).shape[0]) as bar:
    i = 0
    for idx, subsystem in enumerate(bhsList):
        for n in range(0,len(subsystem)):
            if subsystem[n]+"_T6" in df.columns:
                sns.histplot(df[subsystem[n]+"_T6"], ax=ax[n,idx], stat="density", kde=True, alpha=0.3, color="tab:blue")
                ax[n,idx].set_axis_on()

            # to center graph in case T7 is missing
            if (subsystem[n]+"_T6" in df.columns) & (subsystem[n]+"_T7" not in df.columns):
                ax[n,idx].set_xlim(df[subsystem[n]+"_T6"].mean()-(3*df[subsystem[n]+"_T6"].std()),
                            df[subsystem[n]+"_T6"].mean()+(3*df[subsystem[n]+"_T6"].std()))    
            
            
            if subsystem[n]+"_T7" in df.columns:
                sns.histplot(df[subsystem[n]+"_T7"], ax=ax[n,idx], stat="density", kde=True, alpha=0.3, color="tab:orange")
                ax[n,idx].set_axis_on()
                
                ax[n,idx].set_xlim(df[subsystem[n]+"_T7"].mean()-(3*df[subsystem[n]+"_T7"].std()),
                            df[subsystem[n]+"_T7"].mean()+(3*df[subsystem[n]+"_T7"].std()))
            i +=1
            bar.update(i)

for col in range(1,8):
    for row in range(0,4):
        ax[row, col].set_ylabel("")


subsystemsList = ["Lipid", "Metabolic", "Cardio", "Inflammatory", "Renal", "Liver", "Hemato", "Hormonal"]        
for idx, col in enumerate(range(0,8)):
    ax[0, col].set_title(subsystemsList[idx], fontweight="bold")


plt.savefig("../figures/delta_bhs/descriptive_histograms.png", bbox_inches="tight")


#%% plotting residuals 

fig, ax = plt.subplots(
    nrows=4, ncols=8,
    figsize=(21,3.5*4),
    gridspec_kw={"wspace":0.35, "hspace":0.3}
)

for i in fig.axes:
    i.set_axis_off()

behaviour = "AGE"
behaviour2 = "SEX"
with progressbar.ProgressBar(max_value=len(bhsList)) as bar:
    for idx, subsystem in enumerate(bhsList):
        for n in range(0,len(subsystem)):
            if subsystem[n]+"_T6" in df.columns:
                results = smf.ols(
                    formula = f"{subsystem[n]+'_T6'} ~ Q('{behaviour+'_T6'}') + Q('{behaviour2+'_T6'}')", 
                    data=df[pd.notnull(df["PULSE1_T6"])], missing='drop').fit()

                sns.kdeplot(scale(results.resid), ax=ax[n,idx], alpha=0.5, linewidth=2, fill=True)
                ax[n,idx].set_axis_on()
                ax[n,idx].set_xlim(-3.5,3.5)
                ax[n,idx].set_title(subsystem[n])
            
            if subsystem[n]+"_T7" in df.columns:
                results_T7 = smf.ols(
                    formula = f"{subsystem[n]+'_T7'} ~ Q('{behaviour+'_T7'}') + Q('{behaviour2+'_T7'}')", 
                    data=df[pd.notnull(df["PULSE1_T7"])], missing='drop').fit()

                sns.kdeplot(scale(results_T7.resid), ax=ax[n,idx], alpha=0.3, linewidth=2, fill=True, color="tab:orange")
                ax[n,idx].set_axis_on()
            
            if (subsystem[n]+"_T6" not in df.columns) & (subsystem[n]+"_T7" in df.columns):
                ax[n,idx].set_title(subsystem[n])
    
    bar.update(idx)

for col in range(1,8):
    for row in range(0,4):
        ax[row, col].set_ylabel("")

subsystemsList = ["Lipid", "Metabolic", "Cardio", "Inflammatory", "Renal", "Liver", "Hemato", "Hormonal"]        
pad = 20 # in points
for idx, col in enumerate(range(0,8)):
    ax[0, col].annotate(subsystemsList[idx], xy=(0.5,1), xytext=(0,pad),
        fontweight="bold", xycoords='axes fraction', textcoords='offset points',
        size='large', ha='center', va='baseline')

#%% plotting residuals without z-score

fig, ax = plt.subplots(
    nrows=4, ncols=8,
    figsize=(21,3.5*4),
    gridspec_kw={"wspace":0.35, "hspace":0.3}
)

for i in fig.axes:
    i.set_axis_off()

behaviour = "AGE"
behaviour2 = "SEX"
with progressbar.ProgressBar(max_value=len(bhsList)) as bar:
    for idx, subsystem in enumerate(bhsList):
        for n in range(0,len(subsystem)):
            if subsystem[n]+"_T6" in df.columns:
                results = smf.ols(
                    formula = f"{subsystem[n]+'_T6'} ~ Q('{behaviour+'_T6'}') + Q('{behaviour2+'_T6'}')", 
                    data=df[pd.notnull(df["PULSE1_T6"])], missing='drop').fit()

                sns.kdeplot((results.resid), ax=ax[n,idx], alpha=0.5, linewidth=2, fill=True)
                ax[n,idx].set_axis_on()
                ax[n,idx].set_title(subsystem[n])
            
            # to center graph in case T7 is missing
            if (subsystem[n]+"_T6" in df.columns) & (subsystem[n]+"_T7" not in df.columns):
                ax[n,idx].set_xlim(results.resid.mean()-(3*results.resid.std()),
                           results.resid.mean()+(3*results.resid.std()))    
            
            if subsystem[n]+"_T7" in df.columns:
                results_T7 = smf.ols(
                    formula = f"{subsystem[n]+'_T7'} ~ Q('{behaviour+'_T7'}') + Q('{behaviour2+'_T7'}')", 
                    data=df[pd.notnull(df["PULSE1_T7"])], missing='drop').fit()

                sns.kdeplot((results_T7.resid), ax=ax[n,idx], alpha=0.3, linewidth=2, fill=True, color="tab:orange")
                ax[n,idx].set_xlim(results_T7.resid.mean()-(3*results_T7.resid.std()),
                            results_T7.resid.mean()+(3*results_T7.resid.std())) 
                ax[n,idx].set_axis_on()
            
            if (subsystem[n]+"_T6" not in df.columns) & (subsystem[n]+"_T7" in df.columns):
                ax[n,idx].set_title(subsystem[n])
    
    bar.update(idx)

for col in range(1,8):
    for row in range(0,4):
        ax[row, col].set_ylabel("")

subsystemsList = ["Lipid", "Metabolic", "Cardio", "Inflammatory", "Renal", "Liver", "Hemato", "Hormonal"]        
pad = 20 # in points
for idx, col in enumerate(range(0,8)):
    ax[0, col].annotate(subsystemsList[idx], xy=(0.5,1), xytext=(0,pad),
        fontweight="bold", xycoords='axes fraction', textcoords='offset points',
        size='large', ha='center', va='baseline')

plt.savefig("../figures/delta_bhs/descriptive_density_plots_residuals.png", bbox_inches="tight")
#%% 1. liver

fig, ax = plt.subplots(
    nrows=2,
    figsize=(8,6 * 1.618),
    gridspec_kw={"hspace":0.3}
)



sns.kdeplot(df["GGT_T3"], color="tab:blue", fill=True, ax=ax[0])
sns.kdeplot(df["GGT_T4"], color="tab:orange", fill=True, ax=ax[0])
sns.kdeplot(df["GGT_T6"], color="tab:green", fill=True, ax=ax[0])

handles = [mpatches.Patch(facecolor="tab:blue", label="T3"),
           mpatches.Patch(facecolor="tab:orange", label="T4"),
           mpatches.Patch(facecolor="tab:green", label="T6"),
           ]
ax[0].legend(handles=handles)

ax[0].set_xlim(-10,100)
ax[0].set_xlabel("liver - GGT (IU/L)")
ax[0].set_title("Density Plot of GGT")
ax[0].axvline(30, color="red", linestyle="dotted")

ax[1].bar(0, df["liver_T3"].sum(), alpha=0.5)
ax[1].bar(1, df["liver_T4"].sum(), alpha=0.5)
ax[1].bar(2, df["liver_T6"].sum(), alpha=0.5)
ax[1].set_title("Counts of at risk - liver subsystem")
ax[1].set_ylabel("Number individuals (n)")
ax[1].set_xlabel("Study Cohort")
ax[1].xaxis.set_major_locator(MaxNLocator(integer=True))
ax[1].set_xticklabels(["",
    f"T3 > {getQuartile(df['GGT_T3'])}",
    f"T4 > {getQuartile(df['GGT_T4'])}",
    f"T6 > {getQuartile(df['GGT_T6'])}"])


#%%

fig, ax = plt.subplots(
    nrows=2,
    figsize=(8,6 * 1.618),
    gridspec_kw={"hspace":0.3}
)

sns.kdeplot(df["CREATININ_T4"], color="tab:blue", fill=True, ax=ax[0])
sns.kdeplot(df["CREATININ_T5"], color="tab:orange", fill=True, ax=ax[0])
sns.kdeplot(df["CREATININ_T6"], color="tab:green", fill=True, ax=ax[0])
sns.kdeplot(df["CREATININ_T7"], color="tab:red", fill=True, ax=ax[0])

handles = [mpatches.Patch(facecolor="tab:blue", label="T4"),
           mpatches.Patch(facecolor="tab:orange", label="T5"),
           mpatches.Patch(facecolor="tab:green", label="T6"),
           mpatches.Patch(facecolor="tab:red", label="T7"),
           ]
ax[0].legend(handles=handles)

ax[0].set_xlim(20,150)
ax[0].set_xlabel("kidney - serum creatinine (umol/L)")
ax[0].set_title("Density Plot of Creatinine")
ax[0].axvline(120, color="red", linestyle="dotted")

ax[1].bar(0, df["renal_T4"].sum(), alpha=0.5)
ax[1].bar(1, df["renal_T5"].sum(), alpha=0.5)
ax[1].bar(2, df["renal_T6"].sum(), alpha=0.5)
ax[1].bar(3, df["renal_T7"].sum(), alpha=0.5)
ax[1].set_title("Counts of at risk - renal subsystem")
ax[1].set_ylabel("Number individuals (n)")
ax[1].set_xlabel("Study Cohort")
ax[1].xaxis.set_major_locator(MaxNLocator(integer=True))
ax[1].set_xticklabels(["",
    f"T4 > {getQuartile(df['CREATININ_T4'])}",
    f"T5 > {getQuartile(df['CREATININ_T5'])}",
    f"T6 > {getQuartile(df['CREATININ_T6'])}",
    f"T7 > {getQuartile(df['CREATININ_T7'])}"])


#%% cardiac -- change to boxplots for bhs. refactor this to another script

fig, ax = plt.subplots(
    nrows=4,
    figsize=(8,4 * 3 * 1.618),
    gridspec_kw={"hspace":0.3}
)

sns.kdeplot(df["cardiac_T3"], color="tab:gray", fill=True, ax=ax[0])
sns.kdeplot(df["cardiac_T4"], color="tab:blue", fill=True, ax=ax[0])
sns.kdeplot(df["cardiac_T5"], color="tab:orange", fill=True, ax=ax[0])
sns.kdeplot(df["cardiac_T6"], color="tab:green", fill=True, ax=ax[0])
sns.kdeplot(df["cardiac_T7"], color="tab:red", fill=True, ax=ax[0])

handles = [
           mpatches.Patch(facecolor="tab:gray", label="T3"),
           mpatches.Patch(facecolor="tab:blue", label="T4"),
           mpatches.Patch(facecolor="tab:orange", label="T5"),
           mpatches.Patch(facecolor="tab:green", label="T6"),
           mpatches.Patch(facecolor="tab:red", label="T7"),
           ]
ax[0].legend(handles=handles)

ax[0].set_xlim(-0.2,1.2)
ax[0].set_xlabel("Cardiac sub-score")
ax[0].set_title("BHS Cardiac: Pulse, SBP, DBP")
ax[0].axvline(0.33333, color="red", linestyle="dotted")

sns.kdeplot(df["PULSE1_T3"], color="tab:gray", fill= True, ax=ax[1])
sns.kdeplot(df["PULSE1_T4"], color="tab:blue", fill= True, ax=ax[1])
sns.kdeplot(df["PULSE1_T5"], color="tab:orange", fill= True, ax=ax[1])
sns.kdeplot(df["PULSE1_T6"], color="tab:green", fill= True, ax=ax[1])
sns.kdeplot(df["PULSE1_T7"], color="tab:red", fill= True, ax=ax[1])
ax[1].set_title("Density Plot of Pulse Rate over Cohorts")
ax[1].set_xlabel("Pulse Rate (bpm)")
ax[1].set_xlim(35,130)
ax[1].axvline(100, color="red", linestyle="dotted")

sns.kdeplot(df["MEAN_SYSBP_T3"], color="tab:gray", fill= True, ax=ax[2])
sns.kdeplot(df["MEAN_SYSBP_T4"], color="tab:blue", fill= True, ax=ax[2])
sns.kdeplot(df["MEAN_SYSBP_T5"], color="tab:orange", fill= True, ax=ax[2])
sns.kdeplot(df["MEAN_SYSBP_T6"], color="tab:green", fill= True, ax=ax[2])
sns.kdeplot(df["MEAN_SYSBP_T7"], color="tab:red", fill= True, ax=ax[2])
ax[2].set_title("Density Plot of Systolic Blood Pressure over Cohorts")
ax[2].set_xlabel("Systolic Blood Pressure (mmHg)")
ax[2].set_xlim(60,200)
ax[2].axvline(140, color="red", linestyle="dotted")

ax[3].bar(0, (df["cardiac_T3"] > 0.3333).sum(), alpha=0.5)
ax[3].bar(1, (df["cardiac_T4"] > 0.3333).sum(), alpha=0.5)
ax[3].bar(2, (df["cardiac_T5"] > 0.3333).sum(), alpha=0.5)
ax[3].bar(3, (df["cardiac_T6"] > 0.3333).sum(), alpha=0.5)
ax[3].bar(4, (df["cardiac_T7"] > 0.3333).sum(), alpha=0.5)
ax[3].set_title("Counts of at risk - BHS cardiac subsystem scores")
ax[3].set_ylabel("Number individuals (n)")
ax[3].set_xlabel("Study Cohort")
ax[3].xaxis.set_major_locator(MaxNLocator(integer=True))
ax[3].set_xticklabels(["",
    f"T3 > {getQuartile(df['cardiac_T3'])}",
    f"T4 > {getQuartile(df['cardiac_T4']):.2f}",
    f"T5 > {getQuartile(df['cardiac_T5'])}",
    f"T6 > {getQuartile(df['cardiac_T6'])}",
    f"T7 > {getQuartile(df['cardiac_T7'])}"])

