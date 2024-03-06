#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""
loook at contribution to score by subsystem
"""


# In[7]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib

matplotlib.rcParams['font.family'] = ["DejaVu Sans"]
print(matplotlib.__version__)


# In[8]:


df = pd.read_parquet("../data/processed_data/03_ukbb_outcome_bhs_final.parquet")


# In[9]:


df["delta_subsystem_contrib"] = df["delta_subsystem_contrib"].str.replace("_", " ")
df["delta_subsystem_contrib_b"] = df["delta_subsystem_contrib_b"].str.replace("_", " ")
df["delta_biomarker_subsystem_contrib"] = df["delta_biomarker_subsystem_contrib"].str.replace("_", " ")
df["delta_biomarker_subsystem_contrib"] = df["delta_biomarker_subsystem_contrib"].str.replace("delta", "")


# In[10]:


df["delta_subsystem_contrib_b"].unique()


# In[11]:


# rename columns for prettify plot
df.loc[:,"delta_subsystem_contrib"] = df["delta_subsystem_contrib"].replace({
    'cardio score ' : "Cardio subsystem",
    'metabol score ' : "Metabolic subsystem",
    'hepato score ' : "Hepatic subsystem",
    'inflam score ' : "Inflammatory subsystem",
    'renal score ': "Renal subsystem"
})

df.loc[:, "delta_subsystem_contrib_b"] = df["delta_subsystem_contrib_b"].replace({
    'cardio score b ' : "Cardio subsystem",
    'metabol score b ' : "Metabolic subsystem",
    'hepato score b ' : "Hepatic subsystem",
    'inflam score b ' : "Inflammatory subsystem",
    'renal score b ': "Renal subsystem"
})

df.loc[:, "delta_biomarker_subsystem_contrib"] = df["delta_biomarker_subsystem_contrib"].replace({
    ' biomarker cardio score ' : "Cardio subsystem",
    ' biomarker metabol score ' : "Metabolic subsystem",
    ' biomarker hepato score ' : "Hepatic subsystem",
    ' biomarker inflam score ' : "Inflammatory subsystem",
    ' biomarker renal score ': "Renal subsystem"
})


# In[16]:


fig, ax = plt.subplots(
    ncols=3, figsize=(12,3*1.618),
    gridspec_kw = {"wspace":0.0},
    sharey=True
)

df["delta_subsystem_contrib"].value_counts().plot.bar(ax=ax[0], width=0.9)
df["delta_subsystem_contrib_b"].value_counts().plot.bar(ax=ax[1], color="tab:gray", width=0.9)
df["delta_biomarker_subsystem_contrib"].value_counts().plot.bar(color="tab:green", ax=ax[2], width=0.9)


# df[df["sex"]=="Male"]["delta_subsystem_contrib"].value_counts().plot.bar(ax=ax[0], width=1)
# df[df["sex"]=="Male"]["delta_subsystem_contrib_b"].value_counts().plot.bar(ax=ax[1], color="tab:gray", width=1)
# df[df["sex"]=="Male"]["delta_biomarker_subsystem_contrib"].value_counts().plot.bar(color="tab:green", ax=ax[2], width=1)

for i in fig.axes:
    i.tick_params(axis="x", length=0)

ax[0].set_title("Delta BHS", y=1, pad=-14)
ax[1].set_title("Delta BHS (baseline)", y=1, pad=-14)
ax[2].set_title("Delta Biomarker BHS", y=1, pad=-14)

ax[1].tick_params(axis="y", length=0)
ax[2].tick_params(axis="y", length=0)

for i in fig.axes:
    i.set_xticklabels(i.get_xticklabels(), rotation=90, ha='left', va="center", rotation_mode='anchor', fontweight="bold", fontsize=8)
    i.tick_params(axis="x", direction="in", pad=-7, colors="white")

fig.suptitle("Main Subsystem Contribution to Score", fontweight="bold", y=0.935)
plt.savefig("../bhs_figures/subsystem_contrib.png", bbox_inches="tight", dpi=350)


# In[14]:


fig, ax = plt.subplots(
    ncols=3, figsize=(12,3*1.618),
    gridspec_kw = {"wspace":0.0},
    sharey=True
)

df[df["sex"]=="Male"]["delta_subsystem_contrib"].value_counts().plot.bar(ax=ax[0], width=0.9)
df[df["sex"]=="Male"]["delta_subsystem_contrib_b"].value_counts().plot.bar(ax=ax[1], color="tab:gray", width=0.9)
df[df["sex"]=="Male"]["delta_biomarker_subsystem_contrib"].value_counts().plot.bar(color="tab:green", ax=ax[2], width=0.9)

for i in fig.axes:
    i.tick_params(axis="x", length=0)

ax[0].set_title("Delta BHS", y=1, pad=-14)
ax[1].set_title("Delta BHS (baseline)", y=1, pad=-14)
ax[2].set_title("Delta Biomarker BHS", y=1, pad=-14)

ax[1].tick_params(axis="y", length=0)
ax[2].tick_params(axis="y", length=0)

for i in fig.axes:
    i.set_xticklabels(i.get_xticklabels(), rotation=90, ha='left', va="center", rotation_mode='anchor', fontweight="bold", fontsize=8)
    i.tick_params(axis="x", direction="in", pad=-7, colors="white")

fig.suptitle("Main Subsystem Contribution to Score", fontweight="bold", y=0.935)


# In[ ]:





# In[ ]:




