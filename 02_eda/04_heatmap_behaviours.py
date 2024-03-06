#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""
Heatmap of variables in lasso :: looking at the pollution ones in particular 
"""


# In[2]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import re

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OrdinalEncoder

matplotlib.rcParams['font.family'] = ["DejaVu Sans"]


# In[72]:


recodingDict = pd.read_excel("combined_recoding_dict.xlsx")
behavioursDf = pd.read_parquet("bhs_interim_files/behaviours_bhs.parquet")

followedUp = pd.notnull(behavioursDf["pulse_rate.1.0"])
followedDf = behavioursDf.loc[followedUp, :]
followedDf = followedDf.dropna(axis=1, thresh=len(followedDf)*0.70)

exclusionList = ["glycated_haemoglobin","HDL_cholesterol","LDL_direct","triglycerides","systolic_bp","diastolic_bp",
 "pulse_rate","c.reactive_protein","IGF1","creatinine", "cystatin_C", "alanine_aminotransferase", "urea",
 "mean_corpuscular_volume", "aspartate_aminotransferase","gamma_glutamyltransferase", "score", "eid", "delta", "age_group"]

univariateList = followedDf.columns[~followedDf.columns.str.contains("|".join(exclusionList))]


# In[84]:


heatmapDf = followedDf[univariateList]

# cleanup Df and move neighbours
def movePandasCol(df, colName, iloc):
    move_col = df.pop(colName)
    df.insert(iloc, colName, move_col)
    return df

heatmapDf = movePandasCol(heatmapDf, "BMI.0.0", 5)
heatmapDf = movePandasCol(heatmapDf, "weight.0.0", 5)
heatmapDf = movePandasCol(heatmapDf, "genetic_sex.0.0", 5)
heatmapDf = movePandasCol(heatmapDf, "income.0.0", 53)
heatmapDf = movePandasCol(heatmapDf, "own_rent_accomm.0.0", 53)
heatmapDf = movePandasCol(heatmapDf, "population_density.0.0", 53)
heatmapDf = movePandasCol(heatmapDf, "townsend_deprivation_index.0.0", 53)
heatmapDf = movePandasCol(heatmapDf, "sleep_insomnia.0.0", 23)
heatmapDf = movePandasCol(heatmapDf, "seen_psychiatrist.0.0", 23)
heatmapDf = movePandasCol(heatmapDf, "regular_prescription_meds.0.0", 34)
heatmapDf = movePandasCol(heatmapDf, "med_pain_constip_heart.0.0", 34)
heatmapDf = movePandasCol(heatmapDf, "mineral_supplements.0.0", 34)
heatmapDf = movePandasCol(heatmapDf, "number_cancers.0.0", 34)
heatmapDf = movePandasCol(heatmapDf, "number_opertions.0.0", 34)
heatmapDf = movePandasCol(heatmapDf, "number_medications.0.0", 34)
heatmapDf = movePandasCol(heatmapDf, "regular_prescription_meds.0.0", 34)
heatmapDf = movePandasCol(heatmapDf, "overall_health.0.0", 34)
heatmapDf = movePandasCol(heatmapDf, "long_illness_or_disability.0.0", 34)
heatmapDf = movePandasCol(heatmapDf, "employment_status.0.0", 34)
heatmapDf = movePandasCol(heatmapDf, "stress_last_2yrs.0.0", 34)



heatmapDf["genetic_ethnic_grouping.0.0"] = heatmapDf["genetic_ethnic_grouping.0.0"].fillna(value="Other")
enc = Pipeline(steps=[
    ("imputer", SimpleImputer(missing_values=np.nan, strategy="most_frequent")),
    ("encoder", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=np.nan)),
])

heatmapDfEnc = enc.fit_transform(heatmapDf)


# In[42]:


heatmapDf = followedDf[univariateList]


# In[52]:


heatmapDf.head()


# In[77]:


heatmapDf.iloc[:,30]


# In[85]:


correlationMat = np.corrcoef(heatmapDfEnc, rowvar=False)


# In[88]:


fig, ax = plt.subplots(figsize=(15,17)) 

ax.imshow(correlationMat, cmap="Blues")

# Show all ticks and label them with the respective list entries
ax.set_xticks(np.arange(len(correlationMat)))
ax.set_yticks(np.arange(len(correlationMat)))

axLabels = heatmapDf.columns.str.replace(".0.0", "", regex=False).to_list()
axLabels = [re.sub("_", " ", x) for x in axLabels]
ax.set_xticklabels(axLabels)
ax.set_yticklabels(axLabels)

# Rotate the tick labels and set their alignment.
plt.setp(ax.get_xticklabels(), rotation=90, ha="right",
         rotation_mode="anchor")
    
ax.tick_params(axis="both", length=0)

plt.savefig("bhs_figures/behaviours_correlation_matrix.png", bbox_inches="tight", dpi=350)


# In[79]:


heatmapDf.columns.to_list()


# In[ ]:




