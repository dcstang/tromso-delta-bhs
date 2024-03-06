# Adding in DASH Score
# Dietary Approaches to Stop Hypertension
# 
# There are several forms of DASH ranging from 7 - 11 groups across different nationalities
# 1. fruit
# 2. vegetables
# 3. nuts and legumes
# 4. whole grains
# 5. low-fat dairy products
# 6. sodium
# 7. red and processed meats
# 8. sweetened beverages  
# are roughly the several types of categories looked at
# 
# -- need to pull in few dietary factors from UKBB
# we may end up with less categories
# 1. fruit
# 2. vegetables
# 3. grains
# 4. sodium
# 5. red/processed meat
# 6. low-fat dairy  
# 
# range of DASH score between 6 and 30 (6x30)

import pandas as pd
import pyreadr

# %% tags=["parameters"]
upstream = ['Expert variable selection']
product = None

#%%
eidList = pd.read_parquet("~/UKBB/UKB_preparation_in_progress/extraction_recoding/outputs/dash_diet/ukb_final_dash.parquet")
result = pyreadr.read_r("~/UKBB/UKB_preparation_in_progress/extraction_recoding/outputs/dash_diet/ukb_extracted.rds")
dietDf = result[None]
dietDf["eid"] = eidList["eid"].astype("int")

df = pd.read_parquet(upstream['Expert variable selection']['data'])
print(df.shape)

#%%
dietaryVariables =  ["cooked_vegetable_intake.0.0", "raw_vegetable_intake.0.0", 
    "fresh_fruit_intake.0.0", "dried_fruit_intake.0.0", "bread_type.0.0", 
    "cereal_type.0.0",  "pork_intake.0.0", "lamb_mutton_intake.0.0",  
    "processed_meat_intake.0.0", "spread_type.0.0", "milk_type_used.0.0",
    "eid"] 

df = pd.merge(
    df,
    dietDf[dietaryVariables],
    how="left",
    left_on="eid",
    right_on="eid"
)

df.to_parquet(product['data'])



