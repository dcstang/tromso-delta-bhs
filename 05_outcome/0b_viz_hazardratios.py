#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""
Producing hazard ratio plots
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.transforms import ScaledTranslation, Affine2D
from functions.pipelineVariables import upstreamList, studyList
from functions.loadPipelineProducts import getProductFromDag, tidyOutputName

matplotlib.rcParams['font.family'] = ["DejaVu Sans"]

# %% tags=["parameters"]
upstream = ["Cox Regression"]
product = None

#%%
def plotCoxChart(inputDf, ax):   
    if ax is None:
        ax = plt.gca()       

    inputDf = inputDf.convert_dtypes().copy()
    inputDf["lyerr"] = inputDf["coefficient"] - inputDf["95% lower-bound"]
    inputDf["uyerr"] = inputDf["95% upper-bound"] - inputDf["coefficient"]

    trans1 = Affine2D().translate(0.0, -0.15) + ax.transData
    trans2 = Affine2D().translate(0.0, +0.15) + ax.transData
    transformList = [trans1, trans2]

    for idx, bhs_type in enumerate(["delta_bhs", "delta_biomarker_bhs"]):
        plotDf = inputDf[inputDf["covariate"]==bhs_type]
        ax.scatter(plotDf["coefficient"], y=plotDf["adjustment"], transform=transformList[idx])
        ax.errorbar(x=plotDf["coefficient"], y=plotDf["adjustment"], 
                    xerr=[plotDf["lyerr"].to_list(), plotDf["uyerr"].to_list()], 
                    fmt='o', transform=transformList[idx])
        
    ax.invert_yaxis()
    ax.axvline(x=1, linestyle="dotted", color="gray")
    return ax


def getForestPlot(inputDf, title, fileName):
    fig, ax = plt.subplots(
        figsize=(8,4.5*3), nrows=3,
        sharex=True,
        gridspec_kw={"hspace":0.01}
    )

    maleDf = inputDf[inputDf["strata"]=="Male"]
    femaleDf = inputDf[inputDf["strata"]=="Female"]
    allDf = inputDf[inputDf["strata"]=="All"]

    plotCoxChart(maleDf, ax=ax[0])
    plotCoxChart(femaleDf, ax=ax[1])
    plotCoxChart(allDf, ax=ax[2])

    # add symbols 
    ax[0].annotate(u"\u2642", fontname='DejaVu Sans', 
                   xycoords='axes fraction',
                   xy=(0.97, 0.95))
    ax[1].annotate(u"\u2640", fontname='DejaVu Sans', 
                   xycoords='axes fraction',
                   xy=(0.97, 0.95))

    ax[0].set_title(title, fontweight="bold")
    
    fileName = tidyOutputName(fileName, "Calculate")
    fileName = f"output/05_outcome/hazard_forest_plots/{fileName}_{title.lower()}.png"        
    plt.savefig(fileName, dpi=350, bbox_inches="tight")


#%% main
def makeForestPlots(inputDfPath, studyName):
    for outcomeType in ["cancer", "Cad", "CVD"]:
        readExcelPath = tidyOutputName(studyName, "Calculate")
        readExcelPath = f"output/05_outcome/hazard_tables/{readExcelPath}_{outcomeType.lower()}.xlsx"        
        inputDf = pd.read_excel(readExcelPath)
        inputDf = inputDf.fillna("")
        inputDf.columns = ["covariate", "outcome_type", "strata",
                           "adjustment", "coefficient",  "95% lower-bound",
                           "95% upper-bound", "note"]
        getForestPlot(inputDf, outcomeType.upper(), studyName)

for studyType, studyName in zip(studyList, upstreamList):
    print(studyName)
    makeForestPlots(studyType, studyName)