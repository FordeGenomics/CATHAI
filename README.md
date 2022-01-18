# CATHAI
## Notes
* Need to write your own config.py! See the sample config.py included
* Uses shiny server to serve the R shiny apps that are proxied through the authenication dashboard portal
* Make sure that the shiny server is only bound on 127.0.0.1 or that the host has a firewall (either local system or NeCTAR security group e.g.) to block shiny server ports to outside sources

## Docker
### Build
```bash
docker image build --file ./docker/Dockerfile --tag cathai ./docker
```

### Process data
```bash
docker run -p 8080:5000 --mount type=bind,source="./shiny/data/",target="/opt/cathai/shiny/data" cathai 1000 1000 process
```

### Run webapp
```bash
docker run -p 8080:5000 --mount type=bind,source="./shiny/data/",target="/opt/cathai/shiny/data" cathai 1000 1000 run
```

## Setup and running
Setup conda and python modules:
```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
conda create -n cathai -c conda-forge python=3.9 uwsgi=2.0 redis=5.0
conda activate cathai
pip install -r requirements-freeze.txt
```

System libraries (bash):
```bash
apt-get update && apt-get install build-essential libtiff-dev --yes
```

In R:
```R
install.packages(c('flexdashboard','visNetwork','rjson','DT','shinyjs','igraph','stringr','readr','dplyr','ggplot2','ISOweek','EpiCurve','RColorBrewer','gghighlight','imager','bslib','shinydashboard','fresh','tibble','cowplot','parsedate'), repos='https://cran.rstudio.com/')
```

Run standalone (no user accounts):
```bash
./standalone.sh
```

Run dev:
```bash
./local.sh
```

Run prod:
```bash
./prod.sh
```

Setup app database and init admin user defined in config.py:
```bash/python
flask shell
import manager
manager.recreate_db()
manager.setup_prod()
```

Setup nginx reverse proxy for python app, setup LE for prod:
```bash
apt update && apt install nginx
cp cathai.fordelab.com.conf /etc/nginx/sites-available
ln -s /etc/nginx/sites-available/cathai.fordelab.com.conf /etc/nginx/sites-enabled/cathai.fordelab.com.conf
nginx -t && systemctl reload nginx
add-apt-repository ppa:certbot/certbot
apt install python-certbot-nginx
certbot -d cathai.fordelab.com
```

Setup systemctl service for prod:
```
cp cathai.service /etc/systemd/system/
systemctl enable cathai.service
systemctl start cathai.service
```

Setup Shiny Server:
```bash
cp shiny-server.conf /etc/shiny-server/
systemctl restart shiny-server.service
```

* env files and examples
* docker launch script
* move this to wiki and expand