#!/usr/bin/env python
# coding: utf-8

"""
    do a PCA version of biomarker BHS 
    make a continuous version
    remember to do scaling / normalisation 
    label this as delta_biomarker_bhs but make new param in pipeline 
    make it amenable for complete cases or KNN imputation 
    also useful to have diagnostics for PCA - elbow plot and loadings visualisation
    for first attempt do 5 components as representative of subsystems
"""


import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.pipeline import Pipeline
from adjustText import adjust_text
from functions.bhs_calc_functions import getAgeGroupList


def pcaBiomarkerScore(inputDf, deltaColumns, systemNameList, studyName):
    n_components = 5
    ageGroupNameList = ["male_49", "male_50_64", "male_65",
                        "female_49", "female_50_64", "female_65"]
    
    scaler = MinMaxScaler()
    for idx, ageGroup in enumerate(getAgeGroupList(inputDf)):
        pipeline = Pipeline([('scaling', StandardScaler()), 
                         ('pca', PCA(n_components=n_components))])

        inputDf.loc[ageGroup, ["delta_biomarker_"+x+"_score" for x in systemNameList]] = \
            pipeline.fit_transform(inputDf.loc[ageGroup, deltaColumns])
        
        inputDf.loc[ageGroup, ["delta_biomarker_"+x+"_score" for x in systemNameList]] = \
            scaler.fit_transform(inputDf.loc[ageGroup, ["delta_biomarker_"+x+"_score" for x in systemNameList]])
        
        getPcaDiagnostics(pipeline, ageGroupNameList[idx], studyName)
        saveElbowPlot(pipeline, ageGroupNameList[idx], studyName)
        savebiplot(pipeline, ageGroupNameList[idx], studyName, 
                   deltaColumns, adjust=True)

    return inputDf

# one PC per subsystem
def getPcaBhsSubsystem(inputDf, systemNameList, metabol, cardio, inflam, renal, hepato):
    ageGroupNameList = ["male_49", "male_50_64", "male_65",
                            "female_49", "female_50_64", "female_65"]

    pipeline = Pipeline([('scaling', StandardScaler()), 
                         ('pca', PCA(n_components=1))])

    explainedVarList = []

    for idx, ageGroup in enumerate(getAgeGroupList(inputDf)):
        tempExplainedVarList = []
        tempExplainedVarList.append(ageGroupNameList[idx])
        for systemName, bioList in zip(systemNameList, [metabol, cardio, inflam, renal, hepato]):
            inputDf.loc[ageGroup, f"delta_biomarker_{systemName}_score"] = \
                pipeline.fit_transform(inputDf.loc[ageGroup, ["delta_biomarker_" + x for x in bioList]])
            tempExplainedVarList.append('{0:.2f}%'.format(pipeline['pca'].explained_variance_ratio_.sum() * 100))
        explainedVarList.append(tempExplainedVarList)
        
    explainedVarList = pd.DataFrame(explainedVarList, columns=["group"] + systemNameList)    
    return inputDf, explainedVarList

# diagnostics
def getPcaDiagnostics(pipeline, ageGroupName, studyName):
    print(f"{studyName} - {ageGroupName} - {studyName}")
    print("Proportion of Variance Explained : ", pipeline['pca'].explained_variance_ratio_)  
    print("Cumulative Prop. Variance Explained: ", 
           np.cumsum(pipeline['pca'].explained_variance_ratio_))  

          
def saveElbowPlot(pipeline, ageGroupName, studyName):
    PC_values = np.arange(pipeline['pca'].n_components_) + 1
    plt.plot(PC_values, pipeline['pca'].explained_variance_ratio_, 'ro-', linewidth=2)
    plt.title('Scree Plot')
    plt.xlabel('Principal Component')
    plt.ylabel('Proportion of Variance Explained')
    outputPath = 'output/01_data_processing/pca_diagnostics'
    plt.savefig(f'{outputPath}/{studyName}_{ageGroupName}_elbowplot.png')
    plt.close('all')

          
def savebiplot(pipeline, ageGroupName, studyName, labels=None, adjust=False):
    score=pipeline['pca'].components_.T[:,0:2]
    coeff=np.transpose(pipeline['pca'].components_[0:2, :])
    xs = score[:,0]
    ys = score[:,1]
    n = coeff.shape[0]
    scalex = 1.0/(xs.max() - xs.min())
    scaley = 1.0/(ys.max() - ys.min())
    plt.scatter(xs * scalex,ys * scaley, c = "yellow")
    
    texts = []
    for i in range(n):
        plt.arrow(0, 0, coeff[i,0], coeff[i,1],color = 'r',alpha = 0.5)
        if labels is None:
            plt.text(coeff[i,0]* 1.15, coeff[i,1] * 1.15, "Var"+str(i+1), color = 'g', ha = 'center', va = 'center')
        else:
            # plt.text(coeff[i,0]* 1.15, coeff[i,1] * 1.15, labels[i], color = 'g', ha = 'center', va = 'center')
            texts.append(plt.text(coeff[i,0], coeff[i,1], labels[i]))
        
    plt.xlabel("PC{}".format(1))
    plt.ylabel("PC{}".format(2))
    plt.grid()
    
    if adjust:
        adjust_text(texts, arrowprops=dict(arrowstyle="->", color='r', lw=0.5))
    
    outputPath = 'output/01_data_processing/pca_diagnostics'
    plt.savefig(f'{outputPath}/{studyName}_{ageGroupName}_biplot.png')
    plt.close('all')
                         