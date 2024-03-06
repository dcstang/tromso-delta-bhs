import numpy as np
import pandas as pd
import progressbar
import logging
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import statsmodels.formula.api as smf
from datetime import datetime

def getUnivariateResults(var, results):
    varOutput = pd.DataFrame({
                "variable"  : var.replace(".0.0", ""),
                "pval"      : results.pvalues[~results.pvalues.index.str.contains("Intercept|bhs_score")],
                "beta"      : results.params[~results.params.index.str.contains("Intercept|bhs_score")],
                "betaLower" : results.conf_int()[~results.conf_int().index.str.contains("Intercept|bhs_score")][0],
                "betaUpper" : results.conf_int()[~results.pvalues.index.str.contains("Intercept|bhs_score")][1],
                "level"     : results.params[~results.params.index.str.contains("Intercept|bhs_score")].index.str.extract(pat=r"\[(.*?)\]")[0].str.replace("T.", "", regex=False).tolist(),
                "na_50"     : 0,
                "one_cat"   : 0
                })

    return varOutput

def getUnivariatePlotDf(df, variables, outcome, adjustments=None, exclusion_cols=None, logPath=None):
    """
    generate univariate analysis dataframe 
    pull columns from df automatically
    remove bhs biomarkers (change with exclusion_cols)
    add additional filter column, ie. drop other biomarkers
    """
    
    if exclusion_cols is not None:
        variables = variables.drop(exclusion_cols)
        
    outputDfColumns = ["variable", "pval", "beta", "betaLower", "betaUpper", "level", "na_50", "one_cat"]
    outputDf = pd.DataFrame(columns=outputDfColumns)
    dateSuffix = datetime.now().strftime("%d_%m_%y_%H%M")
    
    if logPath is None:
        logging.basicConfig(filename=f'output/03_univariate/lm_debug_{dateSuffix}.txt',
                            level=logging.DEBUG)    
    else:
        logging.basicConfig(filename=f'{logPath}_{dateSuffix}.txt', level=logging.DEBUG)

    for var in progressbar.progressbar(variables):
        if (df[var].isnull().sum())/len(df[var]) > 0.5:
            outputDf.loc[len(outputDf)] = [var,0.0,0.0,0.0,0.0,0.0,1,0]
            continue
        elif len(df[var].unique()) == 1:
            outputDf.loc[len(outputDf)] = [var,0.0,0.0,0.0,0.0,0.0,0,1]
            continue
        else:
            try:
                if adjustments is None:    
                    results = smf.ols(formula = f"{outcome} ~ Q('{var}')", 
                                            data=df, missing='drop').fit()
                elif adjustments is not None:
                    adjustmentVar = adjustments.replace(" + ", "") 
                    results = smf.ols(formula = f"{outcome} ~ Q('{var}') + Q('{adjustmentVar}')", 
                                            data=df, missing='drop').fit()
                outputDf = pd.concat([outputDf, getUnivariateResults(var, results)], 
                                         ignore_index=True)
            except:
                logging.exception(f"An exception was thrown: {var}")
                outputDf.loc[len(outputDf)] = [var,0.0,0.0,0.0,0.0,0.0,-99,-99]

    return outputDf.sort_values("pval", ascending=False)

def baseVolcanoPlot(df, title, ax=None, pointColor="tab:blue", plt_kwargs={}):
    
    if ax is None:
        ax = plt.gca()
        
    bonferroniLevel = -(np.log(0.05/len(df))/np.log(100))
    bonferroniThreshold = 0.05/len(df)
    
    # greyout
    ax.scatter(
        df[df["pval"] > bonferroniThreshold]["beta"],
        -(np.log(df[df["pval"] > bonferroniThreshold]["pval"])/np.log(100)),
        alpha=0.25, linewidth=0, color="grey", **plt_kwargs)
        
    ax.scatter(
        df[df["pval"] < bonferroniThreshold]["beta"],
        -(np.log(df[df["pval"] < bonferroniThreshold]["pval"])/np.log(100)),
        alpha=0.45, linewidth=0, color=pointColor, **plt_kwargs)
        
    ax.axhline(bonferroniLevel, color="black", alpha=0.3, linestyle="dotted")
    # ax.text(x=df["beta"].quantile([0.75]), y= bonferroniLevel * 0.5, s="Bonferroni level", ha="right", alpha=0.3)
    ax.set_xlabel(r"$\beta$ coefficient")
    ax.set_ylabel("$-log_{100}(p_{value})$")
    ax.set_title(title)
    
    return ax


def annotateVolcanoPlot(df, xStart, yStart, yDiff, armLength, nLabel=None, ax=None):
    """
    Annotates volcano plot with connection path to left and right
    """
    if ax is None:
        ax = plt.gca()
    
    if nLabel is not None:
        df = df[df["pval"] != 0]
        df = df.tail(nLabel)
        
    y, dy = yStart, yDiff
    Px, Py = df[df["pval"] < (0.05/len(df))]["beta"], \
        -(np.log(df[df["pval"] < (0.05/len(df))]["pval"])/np.log(100))

    for idx, i in enumerate(Py[~np.isinf(Py)].sort_values(ascending=True).index):
        if (idx % 2 == 0) :
            text = ax.annotate(
                df.loc[i,"FigureName"],
                xy=(Px[i], Py[i]),
                xycoords="data",
                xytext=(xStart, y + idx * dy),
                textcoords="data",
                ha="right",
                fontsize=9,
                arrowprops=dict(
                    arrowstyle="-",
                    color="black",
                    linewidth=0.25,
                    shrinkA=30 + 0.85 * len(df.loc[i,"FigureName"]),
                    shrinkB=5,
                    patchA=None,
                    patchB=None,
                    connectionstyle=f"arc,angleA=-0,angleB=0,armA={-armLength + 3*len(df.loc[i,'FigureName'])},armB=0,rad=0",
                ),
            )
            text.arrow_patch.set_path_effects(
                [path_effects.Stroke(linewidth=1, foreground="white"), path_effects.Normal()]
            )
            
    for idx, i in enumerate(Py[~np.isinf(Py)].sort_values(ascending=True).index):
        if (idx % 2 != 0):
            text = ax.annotate(
                df.loc[i,"FigureName"],
                xy=(Px[i], Py[i]),
                xycoords="data",
                xytext=(-xStart, y + idx * dy),
                textcoords="data",
                ha="left",
                fontsize=9,
                arrowprops=dict(
                    arrowstyle="-",
                    color="black",
                    linewidth=0.25,
                    shrinkA=30 + 0.25 * len(df.loc[i,"FigureName"]),
                    shrinkB=5,
                    patchA=None,
                    patchB=None,
                    connectionstyle=f"arc,angleA=0,angleB=-0,armA={armLength - 3* len(df.loc[i,'FigureName'])},armB=0,rad=0",
                ),
            )
            text.arrow_patch.set_path_effects(
                [path_effects.Stroke(linewidth=1, foreground="white"), path_effects.Normal()]
            )
    return ax

def volcanoPlotCI(df, errorBarAlpha=0.3, errorBarColor="tab:blue", ax=None, errorbar_kwargs={}):
# attempt to plot ci for effect sizes
    if ax is None:
        ax = plt.gca()
        
    errorbarDf = df[df["pval"] < 0.05/len(df)]
    xerrArray = [[beta - lower for beta, lower in zip(errorbarDf["beta"], errorbarDf["betaLower"])],
                [upper - beta for beta, upper in zip(errorbarDf["beta"], errorbarDf["betaUpper"])]]
    
    ax.errorbar(
        errorbarDf["beta"],
        -(np.log(errorbarDf["pval"])/np.log(100)),
        xerr=xerrArray,
        markerstyle=None,
        ls='none',
        color=errorBarColor,
        alpha=errorBarAlpha,
        **errorbar_kwargs 
    )
    
    return ax