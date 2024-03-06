#!/usr/bin/env python
# coding: utf-8

"""
Manhattan plot of univariate analysis
by groups / categories
for all BHS types 
"""

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from statsmodels.stats.multitest import multipletests
from adjustText import adjust_text
from functions.loadPipelineProducts import getProductFromDag, tidyOutputName
from functions.pipelineVariables import upstreamList, studyList
matplotlib.rcParams['font.family'] = ["DejaVu Sans"]


# %% tags=["parameters"]
upstream = ["Univariate analysis on behaviours"]
product = None

# %% declare functions

def getMultipleTestingThreshold(df):
    df.loc[df["pval"]!=0,"bonferroni_significant"] = multipletests(df[df["pval"]!=0]["pval"], method="bonferroni")[0]
    df.loc[df["pval"]!=0, "bh_significant"]        = multipletests(df[df["pval"]!=0]["pval"], method="fdr_bh")[0]
    
    df["bonferroni_significant"] = df["bonferroni_significant"].fillna(value=False)
    df["bh_significant"]         = df["bh_significant"].fillna(value=False)
    
    bonferroni_threshold = multipletests(df[df["pval"]!=0]["pval"], method="bonferroni")[2]
    bh_threshold = df.loc[(df["bh_significant"]==True) & (df["bonferroni_significant"]==False), "pval"].max()
    
    print(f"Bonferroni threshold: {bonferroni_threshold}")
    print(f"Benjamini threshold: {bh_threshold}")
    
    return bonferroni_threshold, bh_threshold


def listCategoryCounts(df):
    for cat in df["Category"].unique():
        print(f"{cat} : {len(df[df['Category']==cat])}")


def preparePlotDf(plotDf):
    plotDf = plotDf[plotDf["pval"]!=0]
    plotDf = plotDf.sort_values('Category')
    plotDf['ind'] = range(len(plotDf))
    plotDf['minuslog10pvalue'] = -np.log10(plotDf.pval)
    plotDf['minuslog10pvalue'] = np.where(np.isinf(plotDf["minuslog10pvalue"]),0,plotDf["minuslog10pvalue"])
    plotDf["Category"] = plotDf["Category"].replace({"Medical condition / Medications": "Medical condition/\nMedications"})
    return plotDf

def manhattanPlot(plotDf, xlabelRotation=0, alignxLabels=True, xlimTuple=None, ax=None):

    bonferroni_level, benjamini_level = getMultipleTestingThreshold(plotDf)
    plotDf = preparePlotDf(plotDf)
    if ax is None:
        ax = plt.gca()

    x_labels = []
    x_labels_pos = []
    for num, (name, group) in enumerate(plotDf.groupby(("Category"))):
        group.plot(kind='scatter', x='ind', y='minuslog10pvalue',color=plt.cm.Dark2(num), ax=ax, s=55, alpha=0.6, lw=0)
        x_labels.append(name)
        x_labels_pos.append((group['ind'].iloc[-1] - (group['ind'].iloc[-1] - group['ind'].iloc[0])/2))

    #     if alignxLabels is True:
    #         x_labels_pos[0] = 1
    #         x_labels_pos[-1] = len(plotDf) -1

    for num, i in enumerate(ax.get_xticklabels()):
        i.set_color(plt.cm.Dark2(num))

    if xlimTuple is not None:
        ax.set_xlim(xlimTuple)
        
    ax.margins(x=0, y=0.01)
    ax.axhline(-np.log10(bonferroni_level), lw=0.5)
    ax.axhline(-np.log10(benjamini_level), lw=0.3)
    ax.set_ylabel("-$log_{10}$(p-value)")
    ax.set_xlabel("")
    ax.set_xticks(x_labels_pos)
    ax.set_xticklabels(x_labels, rotation=xlabelRotation)
    ax.tick_params("x", width=0)
    
    #     if alignxLabels is True:
    #         plt.setp(ax.get_xticklabels()[0], ha="left")
    #         plt.setp(ax.get_xticklabels()[-1], ha="right")

    return ax

def annotateManhattan(plotDf, multiple_testing_type="bonferroni", categoryDrop="/.*/", 
                        limitAnnotNum=None, addLevels=True, protectiveMarker=True,
                        fontSize=10, oneCat=None, ax=None):

    ## annotation of significant points ##
    # choose either bonferroni significant or bh significant only #

    plotDf = preparePlotDf(plotDf)
    plotDf = plotDf[~plotDf["Category"].str.contains(categoryDrop).fillna(False)]
    if multiple_testing_type=="bonferroni":
        plotDf = plotDf[plotDf["bonferroni_significant"]==True]
    elif multiple_testing_type=="benjamini" or multiple_testing_type=="bh":
        plotDf = plotDf[(plotDf["bh_significant"]==True) & (plotDf["bonferroni_significant"]==False)]

    annotDf = plotDf.sort_values("minuslog10pvalue", ascending=False) # if this messes with prepareDF order?? 

    if ax is None:
        ax = plt.gca()

    if oneCat is not None:
        annotDf = annotDf[annotDf["Category"]==oneCat]
        
    if addLevels is True:
        annotDf.loc[annotDf["level"].notnull(), "FigureName"] = annotDf.loc[annotDf["level"].notnull(), "FigureName"] +             "\n $\cdot$ " + annotDf.loc[annotDf["level"].notnull(), "level"]

    if limitAnnotNum is not None:
        annotDf = annotDf.head(limitAnnotNum)

    ax.scatter(annotDf["ind"], annotDf["minuslog10pvalue"],
        color="white", s=55, alpha=0.6, edgecolor="black")
    
    if protectiveMarker is True:
        ax.scatter(annotDf[annotDf["betaUpper"]<0]["ind"], annotDf[annotDf["betaUpper"]<0]["minuslog10pvalue"],
        facecolor="teal", s=20, alpha=1, marker="^")

    longName = annotDf["FigureName"].str.split().str.len() > 3
    annotDf.loc[longName, "FigureName"] = annotDf.loc[longName, "FigureName"].str.split().str.slice(0, 3).str.join(" ") +                 "\n " + annotDf.loc[longName, "FigureName"].str.split().str.slice(3).str.join(" ")
    adjust_text([ax.text(
        i[1]["ind"], i[1]["minuslog10pvalue"],
        i[1]["FigureName"]) for i in annotDf.iterrows()], 
        ax=ax, arrowprops=dict(arrowstyle="-", color='k', lw=0.5), 
        fontsize=fontSize)

    return ax

def getCategoryLength(df, categoryType):
    plotDf = preparePlotDf(df)
    plotDf = plotDf[plotDf["Category"]==categoryType]
    return (plotDf.ind.min(), plotDf.ind.max())


def makeAnnotateManhattanPlots(deltaBHS, deltaBHS_b, deltaBiomarker, outputName):
    fig, ax = plt.subplots(
        figsize=(10,3*3*1.618),
        nrows=3)

    manhattanPlot(deltaBHS, ax=ax[0])
    annotateManhattan(deltaBHS, categoryDrop="Environment", ax=ax[0])

    manhattanPlot(deltaBHS_b, ax=ax[1])
    annotateManhattan(deltaBHS_b, categoryDrop="Environment", limitAnnotNum=10, ax=ax[1])

    manhattanPlot(deltaBiomarker, ax=ax[2])
    annotateManhattan(deltaBiomarker,
                    multiple_testing_type="bonferroni",
                    ax=ax[2], limitAnnotNum=5)

    plt.savefig(f"output/03_univariate/figures/{outputName}_overall_manhattan_plot.png",
                dpi=350, bbox_inches="tight")


def zoomManhattanCategory(deltaBHS, deltaBiomarker, categoryName, outputName):
    fig, ax = plt.subplots(
        nrows=2,
        figsize=(14/2.5,2*2*1.618),
        constrained_layout=True)

    manhattanPlot(deltaBHS, ax=ax[0])
    ax[0].set_xlim(getCategoryLength(deltaBHS, categoryName))
    dbhs_bonferroni, _ = getMultipleTestingThreshold(deltaBHS)
    ax[0].set_ylim(0, -np.log10(dbhs_bonferroni)+4.1)

    annotateManhattan(deltaBHS, multiple_testing_type="benjamini", limitAnnotNum=4,
            addLevels=False, oneCat=categoryName, fontSize=5, ax=ax[0])

    manhattanPlot(deltaBiomarker, ax=ax[1])
    ax[1].set_xlim(getCategoryLength(deltaBHS_b, categoryName))
    dBiomarker_bonferroni, _ = getMultipleTestingThreshold(deltaBiomarker)
    ax[1].set_ylim(0, -np.log10(dBiomarker_bonferroni)+4.1)

    annotateManhattan(deltaBHS_b, multiple_testing_type="benjamini", limitAnnotNum=4,
            addLevels=False, oneCat=categoryName, fontSize=5, ax=ax[1])

    for i in fig.axes:
        i.tick_params("y", width=0)
        
    plt.savefig(f"output/03_univariate/figures/{outputName}_zoom_bonferroni_{categoryName}.png", 
                dpi=350, bbox_inches="tight")


def zoomSeparateCategories(df, studyName, bhsScoreType):
    fig, ax = plt.subplot_mosaic([["m"]*3, ["0", "1", "2"], ["3", "4", "5"]],
                                gridspec_kw=dict(height_ratios=[0.5,2,2]),
                                figsize=(14, 7), constrained_layout=True)

    manhattanPlot(df, ax=ax["m"])
    ax["m"].set_xticklabels([])
    ax["m"].set_ylabel("")
    # ax["m"].set_ylim(0, 8.2) - to set programmatically if neeed

    fig.supylabel("-$log_{10}$(p-value)", ha="right")
    categoryList = ["Behavioural", "Environment", "Individual Traits", 
                    "Medical condition/\nMedications", "Psycho-social",
                    "Socioeconomic"]

    for idx, cat in enumerate(categoryList):
        manhattanPlot(df, ax=ax[str(idx)])

        # settings for different types of categories (ie. specify levels, etc)        
        if idx == 3:
            medConsAdjust = getCategoryLength(df, cat)
            ax[str(idx)].set_xlim(left=medConsAdjust[0]-3, right=medConsAdjust[1]+3)
#         else:
#             ax[str(idx)].set_xlim(getCategoryLength(df, cat))
#             ax[str(idx)].set_ylim(0, -np.log10(dbhs_bonferroni)+0.5)
        
        if idx == 0:
            annotateManhattan(df, multiple_testing_type="bh", limitAnnotNum=2,
                        addLevels=True, oneCat=cat, fontSize=5, ax=ax[str(idx)])
        else:
            annotateManhattan(df, multiple_testing_type="bh", limitAnnotNum=2,
                        addLevels=False, oneCat=cat, fontSize=5, ax=ax[str(idx)])

        ax[str(idx)].set_ylabel("")

    for i in fig.axes:
        i.tick_params("y", width=0)
        
    for i in ["1", "2", "4", "5"]:
        ax[i].set_yticklabels([])
        
    # how to set outputname based on bhs score type??!! 
    plt.savefig(f"output/03_univariate/figures/{studyName}_zoom_all_categories_{bhsScoreType}.png", dpi=350, bbox_inches="tight")



# %% run everything now
for studyName in upstreamList:
    baseOutputPath = f"output/03_univariate/tables/{tidyOutputName(studyName, 'Calculate')}"
    print(studyName)

    deltaBHS = pd.read_csv(f"{baseOutputPath}_lm_deltabhs.csv")
    deltaBHS_b = pd.read_csv(f"{baseOutputPath}_lm_deltabhs_b.csv")
    deltaBiomarker = pd.read_csv(f"{baseOutputPath}_lm_deltabiomarker.csv")

    makeAnnotateManhattanPlots(deltaBHS, deltaBHS_b, deltaBiomarker, tidyOutputName(studyName, 'Calculate'))
    zoomManhattanCategory(deltaBHS, deltaBiomarker, "Environment", tidyOutputName(studyName, 'Calculate'))

    for bhsScoreType, df in zip(["dBHS", "dBHS_b", "dBiomarker"], [deltaBHS, deltaBHS_b, deltaBiomarker]):
        zoomSeparateCategories(df, tidyOutputName(studyName, 'Calculate'), bhsScoreType)