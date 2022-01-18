#!/usr/bin/bash

if [ $# -lt 3 ]; then
    echo "No action supplied. Exiting."
    exit 1
fi

if [ $# -gt 3 ]; then
    echo "More than one action supplied. Exiting."
    exit 1
fi

if [ "$3" = "process" ]; then
    echo "Performing pre-processing on network graphs."
    echo "This may take some time depending on the number of samples"
    source /usr/local/conda/bin/activate /usr/local/conda/envs/cathai
    cd /opt/cathai/shiny
    /opt/cathai/shiny/process_data.py ./data
    echo "Finishing pre-processing."
    echo ""
    echo "Restoring user/group ownership of data folder to ${1}:${2}..."
    chown -R "${1}":"${2}" /opt/cathai/shiny/data
    echo "Done. Thank you for using CATHAI."
    exit 0
fi

if [ "$3" = "run" ]; then
    echo "Starting CATHAI..."

    # set mount point permissions
    echo "Changing file ownership of data folder to restricted user..."
    chown -R www-data:www-data /opt/cathai/shiny/data

    # start nginx
    echo "Launching NGINX web engine..."
    /usr/sbin/nginx -g 'daemon on; master_process on;'

    # start shiny-server as www-data
    echo "Launching Shiny-Server as restricted user..."
    /usr/bin/sudo -u www-data /usr/bin/bash -c 'exec /usr/bin/shiny-server >> /var/log/shiny-server/shiny-server.log 2>&1' &

    # launch cathai_run.sh as www-data
    echo "Launching CATHAI as restricted user..."
    /usr/bin/sudo -u www-data /usr/bin/bash /opt/cathai/cathai_run.sh 1> /opt/cathai/cathai.log 2> /opt/cathai/cathai.err

    echo ""
    echo "Restoring user/group ownership of data folder to ${1}:${2}..."
    chown -R "${1}":"${2}" /opt/cathai/shiny/data
    echo "Done. Thank you for using CATHAI."
    exit 0
fi
