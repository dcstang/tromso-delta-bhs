# %% tags=["parameters"]
upstream = list("Univariate analysis on behaviours")
product = NULL

# %%
#install.packages("sharp", repos="https://cran.ma.imperial.ac.uk/")
#current sharp package used 1.4.6 / 23 Feb 2024
#install.packages("tidyverse", repos="https://cran.ma.imperial.ac.uk/")
library(arrow)
library(sharp)
library(tidyverse)

# %%
pipeline_yaml <- yaml::read_yaml("/rds/general/user/dt20/home/BHS/pipeline.yaml")

studyList <- c('Calculate BHS (Complete Cases)',
            'Calculate BHS (Complete Cases n Lower Quartile Scored)',
            'Calculate BHS (KNN Impute n Lower Quartile Scored)',
            'Calculate BHS (KNN Impute only)',
            'Calculate BHS (Complete Cases n PCA BHS)',
            'Calculate BHS (KNN Impute n PCA BHS)',
            'Calculate BHS (Complete Cases n PCA Subsystem BHS)',
            'Calculate BHS (KNN Impute n PCA Subsystem BHS)',
            'Calculate BHS (Complete Cases n PCA Subsystem BHS Scaled)',
            'Calculate BHS (KNN Impute n PCA Subsystem BHS Scaled)')

tidyOutputString <- function(studyList, clearString){
    studyList <- gsub(clearString, "", studyList)
    studyList <- gsub("\\(|\\)", "", studyList)
    studyList <- str_squish(studyList)
    studyList <- gsub(" ", "_", studyList)
    studyList <- tolower(studyList)
    return(studyList)
}

studyList <- tidyOutputString(studyList, "Calculate")
jobIndex <- as.numeric(Sys.getenv("PBS_ARRAY_INDEX"))

# 11 July 2023: changec this function to accomondate array job
getStab <- function(xDf, yVector, titlePlot, studyType) {
        
        # update 23 Feb 24: include n_cat3 to revert away from loglikelihood estimation
        stab <- VariableSelection(xdata = xDf, ydata = yVector, 
                                  pi_list = seq(0.5, 0.99, by = 0.01), n_cat = 3)
        print(stab)
        png(paste0(
                "output/04_lasso_multivariate/figures/",
                titlePlot, "_", 
                studyType, "_",
                "stability_callibration_one_hot.png"), res=300, width=10, height=4 * 1.618, units="in")
        par(mar = c(7, 5, 7, 6))
        CalibrationPlot(stab)
        dev.off()

        summary(stab)
        cat(paste0(studyType, ",", titlePlot, ",",
                Argmax(stab)[1,2][[1]], "\n"), 
            file="output/04_lasso_multivariate/tables/thresholds.csv",
            append=TRUE)

        m <- as.data.frame(sort(SelectionProportions(stab), decreasing=TRUE))
        colnames(m) <- c("pctSelected")
        write.csv(m, paste0(
                "output/04_lasso_multivariate/tables/",
                titlePlot, "_", 
                studyType, "_",
                "variable_selection_one_hot.csv"))
    
        # output lambda and selection threshold
        cat(Argmax(stab)[1,], file = paste0(
                "output/04_lasso_multivariate/tables/",
                 titlePlot, "_", 
                 studyType, "_lambdaPi_one_hot.txt"))
    
    }

runSharpAllScores <- function(studyType){

        x <- read_parquet(paste0(
                "output/04_lasso_multivariate/data/",
                studyType,
                "_x_one_hot_data.parquet"))
        y <- read_parquet(paste0(
                "output/04_lasso_multivariate/data/",
                studyType,
                "_y_data.parquet"))

        getStab(x, y[,1], "delta_bhs", studyType)
        getStab(x, y[,2], "delta_bhs_b", studyType)
        getStab(x, y[,3], "delta_biomarker", studyType)

}

# now run with PBS_ARRAY_INDEX
runSharpAllScores(studyList[[jobIndex]])