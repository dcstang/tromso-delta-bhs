# %% tags=["parameters"]
upstream = NULL
product = NULL
#

# %%
library(tidyverse)
library(arrow)

df <- read_parquet("~/BHS/data/ukb_final.parquet")
cancerDf <- readRDS("~/UKBB/UKB_preparation_in_progress/outcome_definition/Outputs_cancer/output_final.rds")
cadDf <- readRDS("~/UKBB/UKB_preparation_in_progress/outcome_definition/Outputs_cad/output_final.rds")
cvdDf <- readRDS("~/UKBB/UKB_preparation_in_progress/outcome_definition/Outputs_cvd/output_final.rds")

dim(cancerDf)

cancerDf$eid <- as.integer(cancerDf$eid)
cadDf$eid <- as.integer(cadDf$eid)
cvdDf$eid <- as.integer(cvdDf$eid)

cancerDf <- cancerDf %>%
    rename(
        dateDiagnosisCancer = date_diagnosis,
        dateDeathCancer = date_death,
        caseCancer = case,
        prevalentCancer = prevalent_case,
        incidentCancer = incident_case,
        ttdCancer = time_to_diagnosis
    )

cadDf <- cadDf %>%
    rename(
        dateDiagnosisCad = date_diagnosis,
        dateDeathCad = date_death,
        caseCad = case,
        prevalentCad = prevalent_case,
        incidentCad = incident_case,
        ttdCad = time_to_diagnosis
    )

cvdDf <- cvdDf %>%
    rename(
        dateDiagnosisCVD = date_diagnosis,
        dateDeathCVD = date_death,
        caseCVD = case,
        prevalentCVD = prevalent_case,
        incidentCVD = incident_case,
        ttdCVD = time_to_diagnosis
    )

df <- left_join(
    df,
    cancerDf,
    by="eid"
    )

df <- left_join(
    df,
    cadDf,
    by=c("eid", "date_recr")
)

df <- left_join(
    df,
    cvdDf,
    by=c("eid", "date_recr")
)

head(df)

dim(df)

write_parquet(df, product$data)
