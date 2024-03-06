#!/usr/bin/bash
#/rds/general/user/dt20/home/BHS/04_multivariate/0b_sharp_r_jobs.sh
echo "{{upstream['Hazard ratios forest plot']}}"

RSCRIPTPATH={{resources_['r_script']}}
echo "{{resources_['r_script']}}" >> {{product['output_o']}}
echo "{{resources_['r_script']}}" >> temp_cstat_filepath.txt
echo $RSCRIPTPATH >> {{product['output_o']}}

qsub {{resources_['job_script']}}
echo "Job sent and running $(date)" >> {{product['output_o']}}