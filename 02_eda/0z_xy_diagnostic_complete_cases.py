#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""
plot bhs vs baseline 
complete cases analysis
"""


# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from sklearn.metrics import r2_score
import seaborn as sns
import missingno

matplotlib.rcParams['font.family'] = ["DejaVu Sans"]
print(matplotlib.__version__)


# In[2]:


df = pd.read_parquet("../data/processed_data/04_ukbb_outcome_bhs_diet_complete_cases.parquet")


# In[4]:


fig, ax = plt.subplots(
    figsize=(8, 3*3*1.618),
    nrows=3
)

def plotScatter(x, y, xlabel, ylabel, sCol="tab:blue", ax=None):
    if ax is None:
        ax=plt.gca()
        
    ax.scatter(x,y, alpha=0.15, lw=0, color=sCol)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    
    ax.annotate(
        "$R^2$ = {:.3f}".format(
            r2_score(x, y)), (-0.7, 0.8))
    
    ax.tick_params("both", length=0)
    ax.grid(visible=True, linewidth=0.5, alpha=0.3)
    
    return ax

plotScatter(df["delta_bhs"], df["delta_bhs_b"], "$\Delta$ BHS", "$\Delta$ BHS (Baseline)", ax=ax[0])
plotScatter(df["delta_bhs"], df["delta_biomarker_bhs"], "$\Delta$ BHS", "$\Delta$ Biomarker BHS", "tab:orange", ax=ax[1])
plotScatter(df["delta_bhs_b"], df["delta_biomarker_bhs"],
            "$\Delta$ BHS (Baseline)", "$\Delta$ Biomarker BHS", "tab:red", ax=ax[2])


plt.savefig("diagnostic_r2_plots.png", dpi=350, bbox_inches="tight")


# In[5]:


def plotScatter(x, y, xlabel, ylabel, sCol="tab:blue", ax=None):
    if ax is None:
        ax=plt.gca()
        
    ax.scatter(x,y, alpha=0.15, lw=0, color=sCol)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    
    ax.annotate(
        "$R^2$ = {:.3f}".format(
            r2_score(x, y)), (-0.7, 0.8))
    
    ax.tick_params("both", length=0)
    ax.grid(visible=True, linewidth=0.5, alpha=0.3)
    
    return ax

plotScatter(df["delta_bhs"], df["delta_biomarker_bhs"], "$\Delta$ BHS", "$\Delta$ Biomarker BHS", "tab:orange")


# In[6]:


print(df["incidentCad"].value_counts())
print(df["incidentCancer"].value_counts())


# In[37]:


fig, ax = plt.subplots(
    figsize=(14,10),
    ncols=2,
    nrows=2
)

sns.scatterplot(
    x="delta_bhs", 
    y="delta_biomarker_bhs",
    data=df,
    hue="incidentCVD",
    ax=ax[0,0],
    lw=0,
    alpha=0.3
)

sns.scatterplot(
    x="delta_bhs", 
    y="delta_biomarker_bhs",
    data=df[df["incidentCVD"]==1],
    color="tab:orange",
    lw=0,
    ax=ax[1,0]
)

sns.scatterplot(
    x="delta_bhs", 
    y="delta_biomarker_bhs",
    data=df,
    hue="incidentCancer",
    ax=ax[0,1],
        lw=0,
    alpha=0.3
)

sns.scatterplot(
    x="delta_bhs", 
    y="delta_biomarker_bhs",
    data=df[df["incidentCancer"]==1],
    color="tab:orange",
    lw=0,
    ax=ax[1,1]
)


# In[5]:


for systems in ["cardio", "renal", "hepato", "inflam", "metabol"]:
    df[f"delta_{systems}_score"] = df[f"{systems}_score.1.0"] - df[f"{systems}_score.0.0"]


# In[11]:


# three groups
# 1. deltaBHS < -0.5, deltaBiomarkerBHS < 0.1
# 2. deltaBHS > 0.5, deltaBiomarkerBHS < 0.1
# 3. deltaBHS ~ 0, and deltaBiomarkerBHS ~ 0.6

negativeChange = df[(df["delta_bhs"] < -0.3) & (df["delta_biomarker_bhs"] < 0.2)]
positiveChange = df[(df["delta_bhs"] > 0.3) & (df["delta_biomarker_bhs"] > 0.5)]
noChange = df[((df["delta_bhs"] > -0.05)&(df["delta_bhs"] < 0.05)) & ((df["delta_biomarker_bhs"] < 0.45) & (df["delta_biomarker_bhs"] > 0.35))]


# In[7]:


from scipy.stats import ttest_rel

for systems in ["cardio", "renal", "hepato", "inflam", "metabol"]:
    print(systems)
    print(
        ttest_rel(negativeChange[f"delta_{systems}_score"], negativeChange[f"delta_biomarker_{systems}_score.1.0"])
    )
    print(np.mean(negativeChange[f"delta_{systems}_score"] - negativeChange[f"delta_biomarker_{systems}_score.1.0"]))


# In[36]:


def getSortedDf(inputDf, biomarker):
    outputDf = (inputDf[[f"{biomarker}.0.0", f"{biomarker}.1.0"]]
        .sort_values(by=[f"{biomarker}.0.0", f"{biomarker}.1.0"])
        .melt(ignore_index=False)
        .reset_index())
    outputDf["index"] = outputDf["index"].astype("string")
    
    return outputDf

def getDiffDf(inputDf, biomarker, mainDf):
    outputDf = (
        inputDf[[f"{biomarker}.0.0", f"{biomarker}.1.0"]]
        .sort_values(by=[f"{biomarker}.0.0", f"{biomarker}.1.0"])
        .reset_index())
    outputDf["diff"] = outputDf[f"{biomarker}.1.0"] -                        outputDf[f"{biomarker}.0.0"]
    
    thresholdValue = (mainDf[f"{biomarker}.0.0"] -                      mainDf[f"{biomarker}.1.0"]).quantile([0.75]).values[0]
    
    outputDf["scored"] = np.where(outputDf["diff"] > thresholdValue, 1, 0)
    
    return outputDf


# In[34]:


(df[ "diastolic_bp.1.0"] - df["diastolic_bp.0.0"]).quantile([0.75])


# In[37]:


getDiffDf(plotDf, "diastolic_bp", df)


# In[52]:


fig, ax = plt.subplots(
    figsize=(15, 15),
    nrows=3,
    ncols=3,
    gridspec_kw={"hspace":0,"wspace":0},
    sharey="row"
)

for colNumb, plotDf in enumerate([negativeChange,noChange,positiveChange]):    
    for rowNumb, biomarker in enumerate(["diastolic_bp", "systolic_bp", "pulse_rate"]):
        sns.scatterplot(
            y="value",
            x="index",
            hue="variable",
            data=getSortedDf(plotDf, biomarker),
            ax=ax[rowNumb, colNumb],
            lw=0
        ).set_title(biomarker.replace("_", " "), y=0.92)

        sns.barplot(
            y="diff",
            x="index",
            data=getDiffDf(plotDf, biomarker, df),
            ax=ax[rowNumb, colNumb],
            hue="scored"
        )

for i in fig.axes:
    i.axes.get_xaxis().set_visible(False)
    i.get_legend().remove()
    
plt.savefig("cardio_complete_cases_diagnostics.png", dpi=350, bbox_inches="tight")


# In[51]:


from IPython.display import display
for idx, plotDf in enumerate([negativeChange,noChange,positiveChange]):
    display(plotDf[["pulse_rate.0.0", "pulse_rate.1.0", 
                  "delta_cardio_score", 
                 "delta_biomarker_cardio_score.1.0", 
                  "delta_bhs", "delta_biomarker_bhs"]].head(3))


# In[58]:


fig, ax = plt.subplots(
    figsize=(15, 15),
    nrows=3,
    ncols=3,
    gridspec_kw={"hspace":0,"wspace":0},
    sharey="row"
)

for colNumb, plotDf in enumerate([negativeChange,noChange,positiveChange]):
    for rowNumb, biomarker in enumerate(["alanine_aminotransferase","aspartate_aminotransferase",
                                         "gamma_glutamyltransferase"]):
        sns.scatterplot(
            y="value",
            x="index",
            hue="variable",
            data=getSortedDf(plotDf, biomarker),
            ax=ax[rowNumb, colNumb],
            lw=0
        ).set_title(biomarker.replace("_", " "), y=0.92)
        
        sns.barplot(
            y="diff",
            x="index",
            data=getDiffDf(plotDf, biomarker, df),
            ax=ax[rowNumb, colNumb],
            hue="scored"
        )

for i in fig.axes:
    i.axes.get_xaxis().set_visible(False)
    i.get_legend().remove()
    
plt.savefig("liver_complete_cases_diagnostics.png", dpi=350, bbox_inches="tight")


# In[59]:


fig, ax = plt.subplots(
    figsize=(15, 10),
    nrows=2,
    ncols=3,
    gridspec_kw={"hspace":0,"wspace":0},
    sharey="row"
)

for colNumb, plotDf in enumerate([negativeChange,noChange,positiveChange]):
    for rowNumb, biomarker in enumerate(["creatinine", "cystatin_C"]):
        sns.scatterplot(
            y="value",
            x="index",
            hue="variable",
            data=getSortedDf(plotDf, biomarker),
            ax=ax[rowNumb, colNumb],
            lw=0
        ).set_title(biomarker.replace("_", " "), y=0.92)
        
        sns.barplot(
            y="diff",
            x="index",
            data=getDiffDf(plotDf, biomarker, df),
            ax=ax[rowNumb, colNumb],
            hue="scored"
        )

for i in fig.axes:
    i.axes.get_xaxis().set_visible(False)
    i.get_legend().remove()
    
plt.savefig("renal_complete_cases_diagnostics.png", dpi=350, bbox_inches="tight")


# In[60]:


for idx, plotDf in enumerate([negativeChange,noChange,positiveChange]):
    display(plotDf[["creatinine.0.0", "creatinine.1.0", 
                  "delta_renal_score", 
                 "delta_biomarker_renal_score.1.0", 
                  "delta_bhs", "delta_biomarker_bhs"]].tail(3))


# In[61]:


fig, ax = plt.subplots(
    figsize=(15, 10),
    nrows=2,
    ncols=3,
    gridspec_kw={"hspace":0,"wspace":0},
    sharey="row"
)

for colNumb, plotDf in enumerate([negativeChange,noChange,positiveChange]):
    for rowNumb, biomarker in enumerate(["c.reactive_protein","IGF1"]):
        sns.scatterplot(
            y="value",
            x="index",
            hue="variable",
            data=getSortedDf(plotDf, biomarker),
            ax=ax[rowNumb, colNumb],
            lw=0
        ).set_title(biomarker.replace("_", " "), y=0.92)

        sns.barplot(
            y="diff",
            x="index",
            data=getDiffDf(plotDf, biomarker, df),
            ax=ax[rowNumb, colNumb],
            hue="scored"
        )
for i in fig.axes:
    i.axes.get_xaxis().set_visible(False)
    i.get_legend().remove()
    
plt.savefig("inflam_complete_cases_diagnostics.png", dpi=350, bbox_inches="tight")


# In[13]:





# In[49]:


negativeChange[["diastolic_bp_score.0.0"]].plot.hist()


# In[33]:


df.columns[df.columns.str.contains("score")]


# In[ ]:




