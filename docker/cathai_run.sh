#!/bin/bash

cd /opt/cathai
source /usr/local/conda/bin/activate /usr/local/conda/envs/cathai
honcho start -e standalone.env -f StandAlone
