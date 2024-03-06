#!/usr/bin/bash
# -- script to add all outputs to zip 
# avoiding data files 
# 29 Feb 2024 / David Tang
echo "{{upstream['Univariate analysis manhattan plots', 'Sharp stability selection', 'Models cstat']}}"

zip -r ../output/06_validation/all_results.zip ../output/01_data_processing 
zip -r ../output/06_validation/all_results.zip ../output/02_eda
zip -r ../output/06_validation/all_results.zip ../output/03_univariate/figures
zip -r ../output/06_validation/all_results.zip ../output/03_univariate/figures
zip -r ../output/06_validation/all_results.zip ../output/04_lasso_multivariate/figures
zip -r ../output/06_validation/all_results.zip ../output/04_lasso_multivariate/selection_props
zip -r ../output/06_validation/all_results.zip ../output/04_lasso_multivariate/tables
zip -r ../output/06_validation/all_results.zip ../output/05_outcome/cstat_tables
zip -r ../output/06_validation/all_results.zip ../output/05_outcome/hazard_forest_plots
zip -r ../output/06_validation/all_results.zip ../output/05_outcome/hazard_tables >> {{product['output_o']}}