# Compare c-stat for different BHS scores and datasets
# 2/ get C-stat CIs by bootstrapping 
# 3/ pull into neat latex table 
# 
# structure by saving by KNN impute / Lower quartile scoring 
# to be sent as PBS job   

# %%
library(tidyverse)
library(DescTools)
library(arrow)
library(boot)
library(kableExtra)

# %% tags=["parameters"]
upstream = list("Hazard ratios forest plot")
product = NULL

# %%
pipeline_yaml <- yaml::read_yaml("/rds/general/user/dt20/home/BHS/pipeline.yaml")
source("/rds/general/user/dt20/home/BHS/functions/rloadPipelineProducts.r")

studyNameList <- tidyOutputString(studyNameList, "Calculate")
jobIndex <- as.numeric(Sys.getenv("PBS_ARRAY_INDEX"))

# now get this into a table for exporting / csv
# we need to get dbhs , dbhs_b, and dbiomarker
# make into tibble then do kbl
# seems to take a while to run

FUN <- function(d.set, i, formula) {
   r.glm <- glm(formula, data=d.set[i,], family=binomial)
   Cstat(r.glm)
   }

get_bhs_ci <- function(formulaString, inputDf) {
    boot_dbhs <- boot(inputDf, FUN, formula=as.formula(formulaString), R=999)
    boot_dbhs_ci <- boot.ci(boot_dbhs, type="perc")
    
    return(
        c(formulaString, 
          paste0(round(boot_dbhs$t0, 3), " (",
                 round(boot_dbhs_ci$percent[4],3), ", ",
                 round(boot_dbhs_ci$percent[5],3), ")")))    
}

# use reformulate 
outcomeList <- c("incidentCancer", "incidentCad", "incidentCVD")
termsList <- c("age.0.0", "sex", "bhs_score.0.0")
bhsList <- c("delta_bhs", "delta_bhs_b", "delta_biomarker_bhs")

modelsList <- c()

for (outcomeType in 1:3) {
for (bhsType in 1:3) {
    modelsList <- c(modelsList, reformulate(termsList[1:2], outcomeList[[outcomeType]]))
    modelsList <- c(modelsList, reformulate(c(termsList[1:2], bhsList[[3]]), outcomeList[[outcomeType]]))
    modelsList <- c(modelsList, reformulate(termsList[1:3], outcomeList[[outcomeType]]))
    modelsList <- c(modelsList, reformulate(c(termsList[1:3], bhsList[[bhsType]]), outcomeList[[outcomeType]]))
    }}

modelsList <- unique(modelsList)

# programmatically find dataset
studyTypeDf = read_parquet(
    pipeline_yaml$tasks[[task_location(pipeline_yaml, "Compute DASH")]]$product[[studyList[[jobIndex]]]])
outputMatrix <- sapply(modelsList, get_bhs_ci, inputDf = studyTypeDf)

setNames(as_tibble(t(outputMatrix)), c("Formula", "C-Stat (95% CI)")) %>%
    mutate(across(everything(), as.character)) %>%
    write.csv(paste0("output/05_outcome/cstat_tables/",studyNameList[[jobIndex]],"_models_cstat.csv"))

setNames(as_tibble(t(outputMatrix)), c("Formula", "C-Stat (95% CI)")) %>%
    mutate(across(everything(), as.character)) %>%
    kbl(booktabs = T) %>%
    kable_styling(
        latex_options = c("striped", "hold_position"),
        full_width = F) %>%
    save_kable(paste0("output/05_outcome/cstat_tables/",studyNameList[[jobIndex]],"_models_cstat.pdf"))



