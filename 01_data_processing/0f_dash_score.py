# Adding in DASH Score
# Dietary Approaches to Stop Hypertension
# 
# Coding done by Thomas
# Intention is to summarise UKBB variables into a simpler form  
# potentially avoid bonferroni issues / multiple testing 
# 
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
import numpy as np
from sklearn.impute import KNNImputer
from functions.pipelineVariables import upstreamList, studyList

# %% tags=["parameters"]
#### need to manually update this
upstream = ['Calculate BHS (Complete Cases)',
            'Calculate BHS (Complete Cases n Lower Quartile Scored)',
            'Calculate BHS (KNN Impute n Lower Quartile Scored)',
            'Calculate BHS (KNN Impute only)',
            'Calculate BHS (Complete Cases n PCA BHS)',
            'Calculate BHS (KNN Impute n PCA BHS)',
            'Calculate BHS (Complete Cases n PCA Subsystem BHS)',
            'Calculate BHS (KNN Impute n PCA Subsystem BHS)',
            'Calculate BHS (Complete Cases n PCA Subsystem BHS Scaled)',
            'Calculate BHS (KNN Impute n PCA Subsystem BHS Scaled)'
           ]
product = None


# %% get data
eidList = pd.read_parquet("~/UKBB/UKB_preparation_in_progress/extraction_recoding/outputs/dash_diet/ukb_final_dash.parquet")
result = pyreadr.read_r("~/UKBB/UKB_preparation_in_progress/extraction_recoding/outputs/dash_diet/ukb_extracted.rds")
dietDf = result[None]
dietDf["eid"] = eidList["eid"].astype("int")


# construct DASH
"""
The scoring system is based on quintiles with the lowest intake receiving one point
and the top quintile receiving 5 points for healthy components
for vege intake - quintiles overlap : assign in between score
cooked 
<Q1(<2) - 1, Q2(2-3) : 2.5 points, >Q3 (3+) 5
raw
<Q1 - 1, Q2(1-2) : 2, Q3(2-3) : 3.5, >Q4(3+) 5 
fruit
fresh
<Q1(<1) - 1, Q2(1-2) : 2, Q3(2-3), 3.5, Q4(>3) 5
dried
<Q1(==0) - 1, Q2(0-1) : 2.5, Q3(>1), 5
"""

def assignScoreRecode(df, targetCol, recodeDict):
    return df[targetCol].replace(recodeDict)

def returnDietDf(inputDf, fullDietDf):
    
    dietDf = fullDietDf[fullDietDf["eid"].isin(inputDf["eid"])]
    dietDf = dietDf.replace(-10, 0.5)
    dietDf = dietDf.replace([-1, -3], np.nan)

    knn = KNNImputer().set_output(transform="pandas")
    dietDf = knn.fit_transform(dietDf)

    cookedVegeConds = [dietDf["cooked_vegetable_intake.0.0"] < 2,
    (dietDf["cooked_vegetable_intake.0.0"] >= 2) & (dietDf["cooked_vegetable_intake.0.0"] < 3),
    dietDf["cooked_vegetable_intake.0.0"] >= 3]
    cookedVegePoints = [1, 2.5, 5]

    rawVegeConds = [dietDf["raw_vegetable_intake.0.0"] < 1,
    (dietDf["raw_vegetable_intake.0.0"] >= 1) & (dietDf["raw_vegetable_intake.0.0"] < 2),
    (dietDf["raw_vegetable_intake.0.0"] >= 2) & (dietDf["raw_vegetable_intake.0.0"] < 3),
    dietDf["raw_vegetable_intake.0.0"] >= 3]
    rawVegePoints = [1, 2, 3.5, 5]

    freshFruitConds = [dietDf["fresh_fruit_intake.0.0"] < 1,
    (dietDf["fresh_fruit_intake.0.0"] >= 1) & (dietDf["fresh_fruit_intake.0.0"] < 2),
    (dietDf["fresh_fruit_intake.0.0"] >= 2) & (dietDf["fresh_fruit_intake.0.0"] < 3),
    dietDf["fresh_fruit_intake.0.0"] >= 3]
    freshFruitPoints = rawVegePoints

    driedFruitConds = [dietDf["dried_fruit_intake.0.0"] == 0,
    (dietDf["dried_fruit_intake.0.0"] > 0) & (dietDf["dried_fruit_intake.0.0"] <= 1),
    dietDf["dried_fruit_intake.0.0"] > 1]
    driedFruitPoints = cookedVegePoints
    
    dietDf["bread_type_score"] = assignScoreRecode(dietDf, "bread_type.0.0", 
                            {np.nan:1, 1:3, 2:4, 3:5, 4:2}) 

    dietDf["cereal_type_score"] = assignScoreRecode(dietDf, "cereal_type.0.0", 
                                {np.nan:1, 1:3, 2:2, 3:4, 4:5, 5:1}) 

    dietDf["pork_score"] = assignScoreRecode(dietDf, "pork_intake.0.0", 
                                {np.nan:1, 1:4, 2:3, 3:2, 4:1, 5:1, 0:5}) 

    dietDf["lamb_score"] = assignScoreRecode(dietDf, "lamb_mutton_intake.0.0", 
                                {np.nan:1, 1:4, 2:3, 3:2, 4:1, 5:1, 0:5}) 

    dietDf["processed_meat_score"] = assignScoreRecode(dietDf, "processed_meat_intake.0.0", 
                                {np.nan:1, 1:4, 2:3, 3:2, 4:1, 5:1, 0:5}) 

    dietDf["spead_score"] = assignScoreRecode(dietDf, "spread_type.0.0", 
                                {np.nan:1, 1:2, 2:3, 3:4, 0:5}) 

    dietDf["milk_score"] = assignScoreRecode(dietDf, "milk_type_used.0.0", 
                                {np.nan:1, 1:2, 2:3, 3:4, 4:3, 5:1, 6:5}) 

    dietDf["cooked_vege_score"] = np.select(cookedVegeConds, cookedVegePoints, default=1)
    dietDf["raw_vege_score"] = np.select(rawVegeConds, rawVegePoints, default=1)
    dietDf["fresh_fruit_score"] = np.select(freshFruitConds, freshFruitPoints, default=1)
    dietDf["dried_fruit_score"] = np.select(driedFruitConds, driedFruitPoints, default=1)

    #### 6 categories score ####
    dietDf["GRAIN_SCORE"] = dietDf[["bread_type_score", "cereal_type_score"]].mean(axis=1)
    dietDf["SODIUM_SCORE"] = assignScoreRecode(dietDf, "salt_added_to_food.0.0", 
                                {np.nan:1, 1:5, 2:4, 3:3, 4:2}) 
    dietDf["RED_MEAT_SCORE"] = dietDf[["pork_score", "lamb_score",
                                      "processed_meat_score"]].mean(axis=1)
    dietDf["LOW_FAT_DAIRY_SCORE"] = dietDf[["spead_score", "milk_score"]].mean(axis=1)
    dietDf["VEGE_SCORE"] = dietDf[["cooked_vege_score", "raw_vege_score"]].mean(axis=1)
    dietDf["FRUIT_SCORE"] = dietDf[["fresh_fruit_score", "dried_fruit_score"]].mean(axis=1)

    #### final DASH score !! ####
    dietDf["DASH_SCORE"] = dietDf[[
        "GRAIN_SCORE", "SODIUM_SCORE", "RED_MEAT_SCORE",
        "LOW_FAT_DAIRY_SCORE", "VEGE_SCORE", "FRUIT_SCORE"
    ]].sum(axis=1)

    print(dietDf.iloc[:,-5:-1].tail())
    print(dietDf.shape)
    print(dietDf["DASH_SCORE"].value_counts(bins=5, dropna=False))
    
    return dietDf


def imputeComputeDashScore(inputDfPath, fullDietDf, saveDataPath):
    inputDf = pd.read_parquet(upstream[inputDfPath]['data'])
    dietScoreDf = returnDietDf(inputDf, fullDietDf)
    # TODO: there is issue with merging diet score here. Maybe do join and see
    # lots of missing created
    inputDf = pd.merge(inputDf, dietScoreDf[["eid", "DASH_SCORE"]], how="left", on="eid") 
    print(inputDf["DASH_SCORE"].value_counts(bins=5, dropna=False))
    inputDf.to_parquet(saveDataPath)


# factorise, needed to accomodate multiple inputs
outputPathsList = [product[x] for x in studyList]

for studyType, outputPath in zip(upstreamList, outputPathsList):
    imputeComputeDashScore(studyType, dietDf, outputPath)

