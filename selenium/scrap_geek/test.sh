#!/bin/bash
from_job=$1
to_job=$2
for (( job=$from_job; job<=$to_job; job++ ))
do
  job_name="job${job}"
  echo "$job_name\n"
done
