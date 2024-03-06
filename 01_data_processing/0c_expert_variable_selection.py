"""
Here we want to keep dash score
remove dietary variables

remove behaviours with gender bias - ie. age voice break and balding

EDIT 5 Jan 2023 - ploomber pipelines incorporated
"""

import pandas as pd

# %% tags=["parameters"]
upstream = ['Merge additional behaviours']
product = None

#%%
df = pd.read_parquet(upstream['Merge additional behaviours']['data'])

# remove all intake variables
dietaryVars = ["_intake","veg","fish","diet","egg","salad","fruit","meat",
               "food_weight","portion_size"]
genderVars  = ["bald","voice_break","menopause","HRT","miscarriage",
                "menarche","facial_hair","contraception","hysterectomy_age",
                "pregnant","bilateral_oophorectomy","live_births","oral_contracteption",
                "menstruating_today","pregnancy_termination_no","hysterectomy",
                "oophorectomy_age","primiparous_age","stillbirths_no","gestational_diabetes"]
print(df.shape)
len(df.columns[df.columns.str.contains('|'.join(dietaryVars))])


trimmedDf = df[df.columns[~df.columns.str.contains('|'.join(dietaryVars) + '|' + '|'.join(genderVars))]]

#%%
trimmedDf # 263 variables removed, 218 dietary variables 
trimmedDf.to_parquet(product['data'])

#%% 
print(df.shape)
print(trimmedDf.shape)

