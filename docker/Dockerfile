FROM rocker/shiny:4.1
LABEL maintainer="t.cuddihy1@uq.edu.au"
SHELL [ "/bin/bash", "--login", "-c" ]

COPY ./envs/env_cathai.yml /tmp/

ENV WEB_DIR /opt/cathai
ENV LOG_DIR /var/log/shiny-server
ENV CONDA_DIR /usr/local/conda/

RUN apt-get update && apt-get install nginx git build-essential htop libtiff-dev --yes

RUN R -e "install.packages(c('flexdashboard','visNetwork','rjson','DT','shinyjs','igraph','stringr','readr','dplyr','ggplot2','ISOweek','EpiCurve','RColorBrewer','gghighlight','imager','bslib','shinydashboard','fresh','tibble','cowplot','parsedate'), repos='https://cran.rstudio.com/')"

COPY ./confs/shiny-server.conf /etc/shiny-server/
COPY ./confs/nginx-vhost.conf /etc/nginx/sites-available/default

ENV MINICONDA_VERSION 4.9.2
ADD "https://repo.anaconda.com/miniconda/Miniconda3-py38_${MINICONDA_VERSION}-Linux-x86_64.sh" /tmp/miniconda.sh

RUN chmod +x /tmp/miniconda.sh && \
    /tmp/miniconda.sh -b -p $CONDA_DIR && \
    rm /tmp/miniconda.sh

ENV PATH=$CONDA_DIR/bin:$PATH
RUN echo ". $CONDA_DIR/etc/profile.d/conda.sh" >> ~/.profile
RUN conda init bash

RUN conda update --name base --channel defaults conda
RUN conda env create --file /tmp/env_cathai.yml --force
RUN conda clean --all --yes

RUN echo "Cache hack: kjsl"

RUN git clone -b public https://oauth2:QRrhAFc26hbcx8xBKe8W@gitlab.fordelab.com/binf/cathai.git "${WEB_DIR}"

RUN conda activate cathai && \
    pip install -r "${WEB_DIR}/requirements-freeze.txt" && \
    conda deactivate

COPY ./confs/config.R "${WEB_DIR}/shiny"
COPY ./cathai_run.sh "${WEB_DIR}/cathai_run.sh"
COPY ./cathai_entry.sh "/cathai_entry.sh"

RUN chmod +x "/cathai_entry.sh"
RUN chown -R www-data:www-data "${WEB_DIR}"
RUN chown -R www-data:www-data "${LOG_DIR}"
RUN chown -R www-data:www-data /var/lib/shiny-server

RUN rm -f /tmp/*

ENTRYPOINT ["/usr/bin/bash", "/cathai_entry.sh"]