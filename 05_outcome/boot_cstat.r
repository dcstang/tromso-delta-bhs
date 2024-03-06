
# test one c-stat for dataset 


# install.packages("kableExtra")

library(tidyverse)
library(DescTools)
library(arrow)
library(boot)
library(kableExtra)

df1 <- read_parquet("../data/processed_data/06_ukbb_outcome_trimmed_diet_bhs_complete_cases_dash.parquet")

# colnames(df1)

dbhs_glm <- glm(incidentCVD ~ delta_bhs, data=df1, family=binomial)

Cstat(x=predict(dbhs_glm, method="response"),
     resp = model.response(model.frame(dbhs_glm)))

# calculating bootstrap confidence intervals
FUN <- function(d.set, i, formula) {
   r.glm <- glm(formula, data=d.set[i,], family=binomial)
   Cstat(r.glm)
   }

boot_dbhs <- boot(df1, FUN, formula=as.formula("incidentCVD ~ delta_bhs"), R=999)

boot_dbhs

# get original estimate 
boot_dbhs$t0

boot_dbhs$t0 + 1.96 * 0.01096635

boot.ci(boot_dbhs, type="perc")

boot_dbhs_ci <- boot.ci(boot_dbhs, type="perc")

boot_dbhs_ci$percent

boot_dbhs_ci$percent[4]

boot_dbhs_ci$percent[5]

# now get this into a table for exporting / csv
# we need to get dbhs , dbhs_b, and dbiomarker
# make into tibble then do kbl
# seems to take a while to run

FUN <- function(d.set, i, formula) {
   r.glm <- glm(formula, data=d.set[i,], family=binomial)
   Cstat(r.glm)
   }

get_bhs_ci <- function(inputDf, formulaString, rowName) {
    boot_dbhs <- boot(inputDf, FUN, formula=as.formula(formulaString), R=999)
    boot_dbhs_ci <- boot.ci(boot_dbhs, type="perc")
    
    return(
        c(rowName, formulaString, 
          paste0(round(boot_dbhs$t0, 3), " (",
                 round(boot_dbhs_ci$percent[4],3), ",",
                 round(boot_dbhs_ci$percent[5],3), ")")))    
}


get_bhs_ci(df1, "incidentCancer ~ delta_biomarker_bhs", "Delta Biomarker")

t1 <- get_bhs_ci(df1, "incidentCVD ~ delta_bhs", "Delta BHS")

t2 <- rbind(
    t1, t1, t1
    )

setNames(as_tibble(t2), c("BHS Type", "Formula", "C-Stat (95% CI)")) %>%
kbl(booktabs = T) %>%
kable_styling(
    latex_options = c("striped", "hold_position"),
    full_width = F) %>%
save_kable("test_table.pdf")

# install.packages("magick")


