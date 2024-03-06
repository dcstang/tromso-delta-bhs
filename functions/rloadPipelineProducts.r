# r script store of pipeline variables and functions to reload 

studyNameList <- c('Calculate BHS (Complete Cases)',
            'Calculate BHS (Complete Cases n Lower Quartile Scored)',
            'Calculate BHS (KNN Impute n Lower Quartile Scored)',
            'Calculate BHS (KNN Impute only)',
            'Calculate BHS (Complete Cases n PCA BHS)',
            'Calculate BHS (KNN Impute n PCA BHS)',
            'Calculate BHS (Complete Cases n PCA Subsystem BHS)',
            'Calculate BHS (KNN Impute n PCA Subsystem BHS)'
            )

studyList <- c("data_completeCases_noLowerScore",
    "data_completeCases_yesLowerScore",
    "data_knnImpute_yesLowerScore",
    "data_knnImpute_noLowerScore",
    "data_completeCases_pca",
    "data_knnImpute_pca",
    "data_completeCases_pca_subsystem",
    "data_knnImpute_pca_subsystem"
    )

tidyOutputString <- function(studyList, clearString){
    studyList <- gsub(clearString, "", studyList)
    studyList <- gsub("\\(|\\)", "", studyList)
    studyList <- str_squish(studyList)
    studyList <- gsub(" ", "_", studyList)
    studyList <- tolower(studyList)
    return(studyList)
}

task_location <- function(pipeline_yaml, search_string) {
    task_location = 0
    for (n in seq(length(pipeline_yaml$tasks))) {
        if (pipeline_yaml$tasks[[n]]$name == search_string) {
            task_location = n
    }}
    return(task_location)
}