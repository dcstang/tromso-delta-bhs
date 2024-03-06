# """
# BHS vis - distribution of biomarkers, score and sex+age adjusted distribution
# 1. boxplots of BHS score by age and gender 
# 2. distribution of biomarkers - want this by age + sex adjusted residuals
# """

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
import statsmodels.formula.api as smf
from functions.loadPipelineProducts import getProductFromDag, tidyOutputName
from functions.pipelineVariables import upstreamList, studyList

matplotlib.rcParams['font.family'] = ["DejaVu Sans"]

# %% tags=["parameters"]
upstream = ['Compute DASH']
product = None

# %% 

def getScoreBoxplot(inputDf, sex, studyName):
    """
    simplified boxplots for presentation
        ie. only plot deltaBHS and deltaBiomarker
        want this by sex stratified
        filename is inferred from list of study type names
    """

    fig, ax = plt.subplots(
        ncols=3,
        figsize=(3.8*3,3.8*1.618),
        sharey=True,
        gridspec_kw={"wspace":0.07}
    )

    # melt df for boxplot plotting
    inputDf = inputDf[inputDf["sex"]==sex]
    boxplotPresent = inputDf[["age.0.0", "bhs_score.0.0",
                        "bhs_score.1.0", "delta_bhs", "delta_biomarker_bhs"]]
    boxplotDf = boxplotPresent.melt(id_vars=["age.0.0"], var_name="subsystem")

    def getAgeGroupList(df):
        return([
            (df["age.0.0"] < 50),  
            (df["age.0.0"] >= 50) & (df["age.0.0"] < 64), 
            (df["age.0.0"] >= 64)
        ])

    for idx, ageGroup in enumerate(getAgeGroupList(boxplotDf)):
        sns.boxplot(x="subsystem", y="value", color=plt.cm.Dark2(idx), 
                    data=boxplotDf[ageGroup], ax=ax[idx])

    renameXList = ["Initial BHS","Followup \nBHS",
                "$\Delta$ BHS \n(Toulouse)",
                "$\Delta$ BHS \n(Biomarker)"]

    for i in fig.axes:
        i.tick_params("y", width=0, pad=-1.5)
        i.set_ylabel("")
        i.set_xlabel("")
        i.tick_params("x", width=0, pad=-85)
        i.set_xticklabels(renameXList, rotation=90, ha='left', va="bottom", rotation_mode='anchor', fontsize=8)

    filenameSavePath = f'output/02_eda/figures/score_eda/bhs_boxplots_{tidyOutputName(studyName, "Calculate")}_{sex}.png'
    plt.savefig(filenameSavePath, bbox_inches="tight", dpi=350)


#%% plotting residuals without z-score

def getResidualDensityPlots(inputDf, studyName):
    """
    Distribution of age + sex adjusted residuals
        For all biomarkers organised by subsystem
        filename inferred from list of study type names
    """

    # ORIGINAL BHS LIST
    metabol    = ["glycated_haemoglobin","HDL_cholesterol","LDL_direct","triglycerides"]
    cardio     = ["systolic_bp","diastolic_bp","pulse_rate"]
    inflam     = ["c.reactive_protein","IGF1"]
    renal      = ["creatinine", "cystatin_C"]
    hepato     = ["alanine_aminotransferase","aspartate_aminotransferase","gamma_glutamyltransferase"]

    bhsList = [metabol, cardio, inflam, renal, hepato]

    fig, ax = plt.subplots(
        nrows=4, ncols=5,
        figsize=(16,3.5*4),
        gridspec_kw={"wspace":0.35, "hspace":0.3}
    )

    for i in fig.axes:
        i.set_axis_off()

    behaviour = "age"
    behaviour2 = "sex"
    bhsList = [metabol, cardio, inflam, renal, hepato]
    inputDf["age"] = inputDf["age.0.0"]

    for idx, subsystem in enumerate(bhsList):
        for n in range(0,len(subsystem)):
            if subsystem[n]+".0.0" in inputDf.columns:
                results_t0 = smf.ols(
                    formula = f"Q('{subsystem[n]+'.0.0'}') ~ Q('{behaviour}') + Q('{behaviour2}')", 
                    data=inputDf.loc[:, [behaviour, behaviour2, f"{subsystem[n]+'.0.0'}"]],
                    missing='drop').fit()

                sns.kdeplot((results_t0.resid), ax=ax[n,idx], alpha=0.5, linewidth=2, fill=True)
                ax[n,idx].set_axis_on()
                ax[n,idx].set_title(subsystem[n].replace("_", " "), fontsize=8)            

            
            if subsystem[n]+".1.0" in inputDf.columns:
                results_t1 = smf.ols(
                    formula = f"Q('{subsystem[n]+'.1.0'}') ~ Q('{behaviour}') + Q('{behaviour2}')", 
                    data=inputDf.loc[:, [behaviour, behaviour2, f"{subsystem[n]+'.1.0'}"]],
                    missing='drop').fit()

                sns.kdeplot((results_t1.resid), ax=ax[n,idx], alpha=0.3, linewidth=2, fill=True, color="tab:orange")
                ax[n,idx].set_xlim(results_t1.resid.mean()-(3*results_t1.resid.std()),
                            results_t1.resid.mean()+(3*results_t1.resid.std())) 
                ax[n,idx].set_axis_on()            
    
    for col in range(1,4):
        for row in range(0,3):
            ax[row, col].set_ylabel("")

    subsystemsList = ["Metabolic", "Cardio", "Inflammatory", "Renal", "Liver"]        
    pad = 20 # in points
    for idx, col in enumerate(range(0,5)):
        ax[0, col].annotate(subsystemsList[idx], xy=(0.5,1), xytext=(0,pad),
            fontweight="bold", xycoords='axes fraction', textcoords='offset points',
            size='large', ha='center', va='baseline')

    filenameSavePath = f'output/02_eda/figures/score_eda/biomarker_densityPlots_{tidyOutputName(studyName, "Calculate")}.png'
    plt.savefig(filenameSavePath, bbox_inches="tight", dpi=350)

# %%
def getExploratoryPlotsBHS(studyType, studyName):
    inputDf = pd.read_parquet(getProductFromDag("Compute DASH")[studyType])
    getScoreBoxplot(inputDf, "Male",   studyName)
    getScoreBoxplot(inputDf, "Female", studyName)
    getResidualDensityPlots(inputDf, studyName)

for studyType, studyName in zip(studyList, upstreamList):
    getExploratoryPlotsBHS(studyType, studyName)

# factorise, needed to accomodate multiple inputs
#### edit here to add more studies ####
# outputPathsList = [
#     product["data_completeCases_noLowerScore"],
#     product["data_completeCases_yesLowerScore"]
# ]


###############
# fig, ax = plt.subplots(
#     nrows=4, ncols=5,
#     figsize=(18,3.5*4),
#     gridspec_kw={"wspace":0.3}
# )

# for i in fig.axes:
#     i.set_axis_off()
    
# with progressbar.ProgressBar(max_value=len(bhsList)) as bar:
#     for idx, subsystem in enumerate([metabol, cardio, inflam, renal, hepato]):
#         for n in range(0,len(subsystem)):
#             sns.kdeplot(baseline.loc[followedUp,:].loc[exclusionCriteria, subsystem[n]+".0.0"], ax=ax[n,idx], alpha=0.5, linewidth=2, fill=True)
#             sns.kdeplot(second[subsystem[n]+".1.0"], ax=ax[n,idx], alpha=0.5, linewidth=2, fill=True, color="tab:orange")
#             ax[n,idx].set_xlim(second[subsystem[n]+".1.0"].mean()-(3*second[subsystem[n]+".1.0"].std()),
#                           second[subsystem[n]+".1.0"].mean()+(3*second[subsystem[n]+".1.0"].std()))
#             ax[n, idx].set_axis_on()
#             ax[n, idx].set_title(subsystem[n].replace("_", " "), fontsize=8) 
#             ax[n, idx].set_xlabel("")
#         bar.update(idx)

# for col in range(1,5):
#     for row in range(0,4):
#         ax[row, col].set_ylabel("")

# subsystemsList = ["Metabolic", "Cardio", "Inflammatory", "Renal", "Liver"]        
# pad = 20 # in points
# for idx, col in enumerate(range(0,5)):
#     ax[0, col].annotate(subsystemsList[idx], xy=(0.5,1), xytext=(0,pad),
#         fontweight="bold", xycoords='axes fraction', textcoords='offset points',
#         size='large', ha='center', va='baseline')


# plt.savefig("../bhs_figures/biomarkers_subsystem_distributions.png", dpi=350, bbox_inches="tight")


# # In[9]:


# ## males ##

# fig, ax = plt.subplots(
#     nrows=4, ncols=5,
#     figsize=(18,3.5*4),
#     gridspec_kw={"wspace":0.3}
# )

# for i in fig.axes:
#     i.set_axis_off()
    
# with progressbar.ProgressBar(max_value=len(bhsList)) as bar:
#     for idx, subsystem in enumerate([metabol, cardio, inflam, renal, hepato]):
#         for n in range(0,len(subsystem)):
#             sns.kdeplot(baseline.loc[followedUp,:].loc[exclusionCriteria,:].loc[baseline["sex"]=="Male", subsystem[n]+".0.0"],
#                         ax=ax[n,idx], alpha=0.5, linewidth=2, fill=True)
#             sns.kdeplot(second.loc[second["sex"]=="Male", subsystem[n]+".1.0"],
#                         ax=ax[n,idx], alpha=0.5, linewidth=2, fill=True, color="tab:orange")
#             ax[n,idx].set_xlim(second.loc[second["sex"]=="Male", subsystem[n]+".1.0"].mean() -                                (3*second.loc[second["sex"]=="Male", subsystem[n]+".1.0"].std()),
#                           second.loc[second["sex"]=="Male", subsystem[n]+".1.0"].mean() + \
#                                (3*second.loc[second["sex"]=="Male", subsystem[n]+".1.0"].std()))
            
#             ax[n, idx].set_axis_on()
#             ax[n, idx].set_title(subsystem[n].replace("_", " "), fontsize=8) 
#             ax[n, idx].set_xlabel("")
#         bar.update(idx)

# for col in range(1,5):
#     for row in range(0,4):
#         ax[row, col].set_ylabel("")

# subsystemsList = ["Metabolic", "Cardio", "Inflammatory", "Renal", "Liver"]        
# pad = 20 # in points
# for idx, col in enumerate(range(0,5)):
#     ax[0, col].annotate(subsystemsList[idx], xy=(0.5,1), xytext=(0,pad),
#         fontweight="bold", xycoords='axes fraction', textcoords='offset points',
#         size='large', ha='center', va='baseline')


# plt.savefig("../bhs_figures/biomarkers_subsystem_distributions_male.png", dpi=350, bbox_inches="tight")


# # In[10]:


# ## females ##

# fig, ax = plt.subplots(
#     nrows=4, ncols=5,
#     figsize=(18,3.5*4),
#     gridspec_kw={"wspace":0.3}
# )

# for i in fig.axes:
#     i.set_axis_off()
    
# with progressbar.ProgressBar(max_value=len(bhsList)) as bar:
#     for idx, subsystem in enumerate([metabol, cardio, inflam, renal, hepato]):
#         for n in range(0,len(subsystem)):
#             sns.kdeplot(baseline.loc[followedUp,:].loc[exclusionCriteria,:].loc[baseline["sex"]=="Female", subsystem[n]+".0.0"],
#                         ax=ax[n,idx], alpha=0.5, linewidth=2, fill=True)
#             sns.kdeplot(second.loc[second["sex"]=="Female", subsystem[n]+".1.0"],
#                         ax=ax[n,idx], alpha=0.5, linewidth=2, fill=True, color="tab:orange")
#             ax[n,idx].set_xlim(second.loc[second["sex"]=="Female", subsystem[n]+".1.0"].mean() -                                (3*second.loc[second["sex"]=="Female", subsystem[n]+".1.0"].std()),
#                           second.loc[second["sex"]=="Male", subsystem[n]+".1.0"].mean() + \
#                                (3*second.loc[second["sex"]=="Female", subsystem[n]+".1.0"].std()))
            
#             ax[n, idx].set_axis_on()
#             ax[n, idx].set_title(subsystem[n].replace("_", " "), fontsize=8) 
#             ax[n, idx].set_xlabel("")
#         bar.update(idx)

# for col in range(1,5):
#     for row in range(0,4):
#         ax[row, col].set_ylabel("")

# subsystemsList = ["Metabolic", "Cardio", "Inflammatory", "Renal", "Liver"]        
# pad = 20 # in points
# for idx, col in enumerate(range(0,5)):
#     ax[0, col].annotate(subsystemsList[idx], xy=(0.5,1), xytext=(0,pad),
#         fontweight="bold", xycoords='axes fraction', textcoords='offset points',
#         size='large', ha='center', va='baseline')


# plt.savefig("../bhs_figures/biomarkers_subsystem_distributions_female.png", dpi=350, bbox_inches="tight")










