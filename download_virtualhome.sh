#!/usr/bin/env bash

aws s3 cp --recursive s3://geniehai/jackiey/virtualhome/ .
unzip virtualhome_linux_Data.zip
unzip programs_processed_precond_nograb_morepreconds.zip
chmod +x virtualhome_linux.x86_64