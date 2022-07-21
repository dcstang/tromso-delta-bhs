#%%

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.transforms import Affine2D
from matplotlib.patches import Patch
import statsmodels.formula.api as smf
import matplotlib.patheffects as path_effects
import progressbar
import numpy as np


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
misc       = ["DATE", "delta_bhs", "_b", "_score", 
                "cardio|metabol|renal|hepato|hemato|lipid|hormone"]

markersList = lipid + metabol + cardio + inflam + renal + hemato + hormone + misc

behaviourCols = outcomeDf.columns[~outcomeDf.columns.str.contains('|'.join(markersList))]
print(len(behaviourCols))


#%% volcano plot Df
lmOutputDf = pd.DataFrame(columns=["var", "pval", "beta", "betaLower", "betaUpper"])

for behaviour in progressbar.progressbar(behaviourCols):
    try:
        results = smf.ols(formula = f"delta_bhs ~ Q('{behaviour}')", 
                        data=outcomeDf.loc[:, :][["delta_bhs", f"{behaviour}"]], missing='drop').fit()
        lmOutputDf.loc[len(lmOutputDf)] = [behaviour, results.pvalues[-1], 
                                        results.params[-1], results.conf_int()[0][-1], results.conf_int()[1][-1]]
    except:
        lmOutputDf.loc[len(lmOutputDf)] = [behaviour,0.0,0.0,0.0,0.0]

#%%

fig, ax = plt.subplots(
    figsize=(12, 5 * 1.618)
)

bonferroniLevel = -(np.log(0.05/len(behaviourCols))/np.log(100))

# greyout
ax.scatter(
    lmOutputDf[lmOutputDf["pval"] > (0.05/len(behaviourCols))]["beta"],
    -(np.log(lmOutputDf[lmOutputDf["pval"] > (0.05/len(behaviourCols))]["pval"])/np.log(100)),
    alpha=0.25, linewidth=0, color="grey")

ax.scatter(
    lmOutputDf[lmOutputDf["pval"] < (0.05/len(behaviourCols))]["beta"],
    -(np.log(lmOutputDf[lmOutputDf["pval"] < (0.05/len(behaviourCols))]["pval"])/np.log(100)),
    alpha=0.45, linewidth=0, color="tab:blue")

ax.axhline(bonferroniLevel, color="black", alpha=0.3, linestyle="dotted")
ax.set_xlim(-0.38,0.38)
ax.text(x=0.35, y=bonferroniLevel * 0.3, s="Bonferroni level", ha="right", alpha=0.3)

y, dy = 2.35, 1

Px, Py = lmOutputDf[lmOutputDf["pval"] < (0.05/len(behaviourCols))]["beta"], \
    -(np.log(lmOutputDf[lmOutputDf["pval"] < (0.05/len(behaviourCols))]["pval"])/np.log(100))

for idx, i in enumerate(Py[~np.isinf(Py)].sort_values(ascending=True).index):
    if (idx % 2 == 0) :
        text = ax.annotate(
            lmOutputDf.loc[i,"var"].lower().replace("_", " ").replace("t6", "").replace("t7", ""),
            xy=(Px[i], Py[i]),
            xycoords="data",
            xytext=(0.35, y + idx * dy),
            textcoords="data",
            ha="right",
            arrowprops=dict(
                arrowstyle="-",
                color="black",
                linewidth=0.25,
                shrinkA=30 + 0.85 * len(lmOutputDf.loc[i,"var"]),
                shrinkB=5,
                patchA=None,
                patchB=None,
                connectionstyle=f"arc,angleA=-0,angleB=0,armA={-170 + 3*len(lmOutputDf.loc[i,'var'])},armB=0,rad=0",
            ),
        )
        text.arrow_patch.set_path_effects(
            [path_effects.Stroke(linewidth=1, foreground="white"), path_effects.Normal()]
        )

for idx, i in enumerate(Py[~np.isinf(Py)].sort_values(ascending=True).index):
    if (idx % 2 != 0):
        text = ax.annotate(
            lmOutputDf.loc[i,"var"].lower().replace("_", " ").replace("t6", "").replace("t7", ""),
            xy=(Px[i], Py[i]),
            xycoords="data",
            xytext=(-0.35, y + idx * dy),
            textcoords="data",
            ha="left",
            arrowprops=dict(
                arrowstyle="-",
                color="black",
                linewidth=0.25,
                shrinkA=30 + 0.25 * len(lmOutputDf.loc[i,"var"]),
                shrinkB=5,
                patchA=None,
                patchB=None,
                connectionstyle=f"arc,angleA=0,angleB=-0,armA={170 - 3*len(lmOutputDf.loc[i,'var'])},armB=0,rad=0",
            ),
        )
        text.arrow_patch.set_path_effects(
            [path_effects.Stroke(linewidth=1, foreground="white"), path_effects.Normal()]
        )

ax.set_xlabel(r"$\beta$ coefficient")
ax.set_ylabel("$-log_{100}(p_{value})$")
ax.set_title(r"$\Delta$ BHS Volcano Plot")

plt.savefig("../figures/delta_bhs/volcano_plot_delta_bhs.png", bbox_inches="tight")


#%% ZOOMED VERSION OF ABOVE
# TODO: combine into subplots with connection path in future 

fig, ax = plt.subplots(
    figsize=(12, 4 * 1.618)
)

bonferroniLevel = -(np.log(0.05/len(behaviourCols))/np.log(100))

# greyout
ax.scatter(
    lmOutputDf[lmOutputDf["pval"] > (0.05/len(behaviourCols))]["beta"],
    -(np.log(lmOutputDf[lmOutputDf["pval"] > (0.05/len(behaviourCols))]["pval"])/np.log(100)),
    alpha=0.25, linewidth=0, color="grey")

ax.scatter(
    lmOutputDf[lmOutputDf["pval"] < (0.05/len(behaviourCols))]["beta"],
    -(np.log(lmOutputDf[lmOutputDf["pval"] < (0.05/len(behaviourCols))]["pval"])/np.log(100)),
    alpha=0.45, linewidth=0, color="tab:blue")

ax.axhline(bonferroniLevel, color="black", alpha=0.3, linestyle="dotted")
ax.set_xlim(-0.38,0.38)
ax.set_ylim(-0.3,8)
ax.text(x=0.35, y=bonferroniLevel * 0.5, s="Bonferroni level", ha="right", alpha=0.3)

y, dy = 2.35, 0.15

Px, Py = lmOutputDf[lmOutputDf["pval"] < (0.05/len(behaviourCols))]["beta"], \
    -(np.log(lmOutputDf[lmOutputDf["pval"] < (0.05/len(behaviourCols))]["pval"])/np.log(100))

for idx, i in enumerate(Py[~np.isinf(Py)].sort_values(ascending=True).index):
    if (idx % 2 == 0) :
        text = ax.annotate(
            lmOutputDf.loc[i,"var"].lower().replace("_", " ").replace("t6", "").replace("t7", ""),
            xy=(Px[i], Py[i]),
            xycoords="data",
            xytext=(0.35, y + idx * dy),
            textcoords="data",
            ha="right",
            arrowprops=dict(
                arrowstyle="-",
                color="black",
                linewidth=0.25,
                shrinkA=30 + 0.85 * len(lmOutputDf.loc[i,"var"]),
                shrinkB=5,
                patchA=None,
                patchB=None,
                connectionstyle=f"arc,angleA=-0,angleB=0,armA={-170 + 3*len(lmOutputDf.loc[i,'var'])},armB=0,rad=0",
            ),
        )
        text.arrow_patch.set_path_effects(
            [path_effects.Stroke(linewidth=1, foreground="white"), path_effects.Normal()]
        )

for idx, i in enumerate(Py[~np.isinf(Py)].sort_values(ascending=True).index):
    if (idx % 2 != 0):
        text = ax.annotate(
            lmOutputDf.loc[i,"var"].lower().replace("_", " ").replace("t6", "").replace("t7", ""),
            xy=(Px[i], Py[i]),
            xycoords="data",
            xytext=(-0.35, y + idx * dy),
            textcoords="data",
            ha="left",
            arrowprops=dict(
                arrowstyle="-",
                color="black",
                linewidth=0.25,
                shrinkA=30 + 0.25 * len(lmOutputDf.loc[i,"var"]),
                shrinkB=5,
                patchA=None,
                patchB=None,
                connectionstyle=f"arc,angleA=0,angleB=-0,armA={170 - 3*len(lmOutputDf.loc[i,'var'])},armB=0,rad=0",
            ),
        )
        text.arrow_patch.set_path_effects(
            [path_effects.Stroke(linewidth=1, foreground="white"), path_effects.Normal()]
        )

ax.set_xlabel(r"$\beta$ coefficient")
ax.set_ylabel("$-log_{100}(p_{value})$")
ax.set_title(r"$\Delta$ BHS Volcano Plot (ZOOMED)")
plt.savefig("../figures/delta_bhs/volcano_plot_delta_bhs_zoomed.png", bbox_inches="tight")