"""
Refactoring code 

Old visualisation code for biomarker/subsystems distibution
Code from June 2022
"""



#%% 1. liver - ggt + albumin

for colnames in df.columns[
    df.columns.str.contains("GGT") & ~df.columns.str.contains("42")]:
    timeFrame = colnames[-2:]
    _quartileCutOff = getQuartile(df[colnames])

    df[f"liver_{timeFrame}"] = df[colnames].apply(lambda x: True if (x > _quartileCutOff) else False)

#%% 2. renal - creatinin, cystatin_c

for colnames in df.columns[
    df.columns.str.contains("CREATININ") & ~df.columns.str.contains("42|72")]:
    timeFrame = colnames[-2:]
    _quartileCutOff = getQuartile(df[colnames])

    df[f"renal_{timeFrame}"] = df[colnames].apply(lambda x: True if (x > _quartileCutOff) else False)

#%% cardiac 

for colnames in df.columns[
    df.columns.str.contains("PULSE1") & ~df.columns.str.contains("42")]:
    timeFrame = colnames[-2:]
    _quartileCutOff = getQuartile(df[colnames])

    df[f"cardiac_a_{timeFrame}"] = df[colnames].apply(lambda x: True if (x > _quartileCutOff) else False)

for colnames in df.columns[
    df.columns.str.contains("MEAN_SYSBP") & ~df.columns.str.contains("42")]:
    timeFrame = colnames[-2:]
    _quartileCutOff = getQuartile(df[colnames])

    df[f"cardiac_b_{timeFrame}"] = df[colnames].apply(lambda x: True if (x > _quartileCutOff) else False)

for colnames in df.columns[
    df.columns.str.contains("MEAN_DIABP") & ~df.columns.str.contains("42")]:
    timeFrame = colnames[-2:]
    _quartileCutOff = getQuartile(df[colnames])

    df[f"cardiac_c_{timeFrame}"] = df[colnames].apply(lambda x: True if (x > _quartileCutOff) else False)

#%% sum cardiac
for timeframe in ["T3", "T4", "T5", "T6", "T7"]:
    print(f"cardiac_{timeframe}")
    df[f"cardiac_{timeframe}"] = (df[f"cardiac_a_{timeframe}"].astype(float) + 
                                    df[f"cardiac_b_{timeframe}"].astype(float) +
                                    df[f"cardiac_c_{timeframe}"].astype(float))/3



