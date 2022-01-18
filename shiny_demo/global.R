# server
library(ggplot2)
library(tibble)
library(grid)
library(cowplot)
library(visNetwork)
library(rjson)
library(shinyjs)
library(igraph)
library(stringr)
library(readr)
library(dplyr)
library(ISOweek)
library(EpiCurve)
library(RColorBrewer)
library(gghighlight)
library(imager)
library(DT)

# ui
library(shinyjs)
library(shinydashboard)
library(fresh)
library(parsedate)

source('config.R')

sST <- list.files(data_dir, pattern = "*.snpDists.json") %>%
  str_remove(".snpDists.json") %>%
  str_replace("_ST[_]?", " ST") %>%
  str_split(" ")
sST = as.data.frame(do.call(rbind, sST))
sST$V1 = str_replace_all(sST$V1, "_", " ")
sST$V2 = str_replace(sST$V2, "STNA", "NA")

sST.json = list()

for(species in unique(sST$V1))
{
  sST.json[species] <- list(sST[sST$V1 == species,]$V2)
}

clusters <- read.csv(cluster_file, stringsAsFactors = FALSE, na.strings = "")
if (nrow(clusters) > 0){
  clusters$MEMBERS <- strsplit(clusters$MEMBERS, ";")
}
latest_dir <- data_dir

legend_data <- tibble(x = 1:4, y = 1,
                      label = c("Sample", "Selected", "Cluster", "Highlighted"),
                      colour = c(node.colours$background, selected.colours$background, cluster.colours$background, show.colours$background))

legend_data <- tibble(x = 1:4, y = 1,
                      label = c("Sample", "Selected", "Cluster", "Highlighted"),
                      colour = c(node.colours$background, selected.colours$background, cluster.colours$background, show.colours$background))

cols <- as.character(legend_data$colour)
names(cols) <- legend_data$label

legend_dummy <- ggplot(legend_data, aes(x=x, y=y, color=label)) +
  geom_point(shape=19, size=16) +
  scale_color_manual(values = cols, name=NULL, aesthetics = c("colour", "fill"),
                     limits=c("Sample", "Selected", "Highlighted", "Cluster")) +
  theme(legend.key = element_rect(colour = 'white', fill = 'white')) +
  guides(color = guide_legend(title.position = "top", title.hjust = 0.5, label.position = "bottom"))
legend <- get_legend(legend_dummy)

mobile_legend_dummy <- ggplot(legend_data, aes(x=x, y=y, color=label)) +
  geom_point(shape=19, size=8) +
  scale_color_manual(values = cols, name=NULL, aesthetics = c("colour", "fill"),
                     limits=c("Sample", "Selected", "Highlighted", "Cluster")) +
  theme(legend.key = element_rect(colour = 'white', fill = 'white'), legend.position="bottom") +
  guides(color = guide_legend(title.position = "top", title.hjust = 0.5, label.position = "left"))
mobile_legend <- get_legend(mobile_legend_dummy)

node_colour_choices = c('Default', 'SNP Distance From Selected', 'Sample Date', 'Hospital', 'Site')
edge_colour_choices = c('Default', 'SNP Distance', 'Delta Days')
