function(input, output, session) {
  values <- reactiveValues()

  species <- default_species
  st <- default_st

  identify_cluster <- function(s1, ...){
    ret <- clusters[apply(clusters, 1, function(x) s1 %in% x['MEMBERS'][[1]]), ]$CLUSTER
    if (length(ret) == 0) return("")
    if (length(ret) == 1) return(ret)
    return(paste(ret, collapse = '|'))
  }

  get_default_node_colours <- function(nodes){
    print("function: get_default_node_colours")

    species <- input$speciesSelect
    st <- input$stSelect

    species <- gsub('_', ' ', species)
    st <- gsub('ST', '', st)
    if (st == '_NA') st <- "NA"
    sST.clusters <- clusters[clusters$SPECIES == species & clusters$ST == st, ]

    # default all to base
    nCols <- nrow(nodes)
    nodes$color <- rep(list(node.colours),nCols)

    # if cluster set, change those only
    cluster <- input$selectCluster
    if (!is.null(cluster) && cluster != '' && cluster %in% sST.clusters$CLUSTER) {
      nCols <- nrow(nodes[which(nodes$ID %in% sST.clusters[sST.clusters$CLUSTER == cluster, ]$MEMBERS[[1]]), ])
      nodes[which(nodes$ID %in% sST.clusters[sST.clusters$CLUSTER == cluster, ]$MEMBERS[[1]]), ]$color <- rep(list(cluster.colours),nCols)
    }

    # if show nodes set, change those only
    sel_nodes <- input$selectNodes
    if (!is.null(sel_nodes) && sel_nodes != '' && nrow(nodes[which(nodes$ID %in% sel_nodes), ]) > 0) {
      nCols <- nrow(nodes[which(nodes$ID %in% sel_nodes), ])
      nodes[which(nodes$ID %in% sel_nodes), ]$color <- rep(list(show.colours),nCols)
    }

    return(nodes)
  }

  get_node_colours <- function(nodes){
    print("function: get_node_colours")
    if (is.null(nodes)) {return(nodes)}

    species <- input$speciesSelect
    st <- input$stSelect
    if (is.null(species) || is.null(st)) return(NULL)
    if (species == "" || st == "") return(NULL)

    if (input$edgeColour == "Default"){
      return(get_default_node_colours(nodes))
    }
  }

  get_nodes <- function(){
    print("function: get_nodes")
    species <- input$speciesSelect
    st <- input$stSelect
    if (is.null(species) || is.null(st)) return(NULL)
    if (species == "" || st == "") return(NULL)
    species <- gsub(' ', '_', species)
    if (st == 'NA') st <- gsub('NA', 'ST_NA', st)
    path <- paste0(latest_dir, species, "_", st, ".snpDists.json")
    node.json <- fromJSON(file = path)
    nodes <- as.data.frame(node.json[[2]])
    nodes$label <- ""
    nodes$id <- nodes$ID
    nodes$title <- nodes$ID
    nodes$date <- as.Date(parsedate::parse_date(nodes$sample.date))
    nodes <- get_node_colours(nodes)
    values$nodes <- nodes
    return(nodes)
  }

  get_species_nodes <- function(){
    print("function: get_species_nodes")
    species <- input$speciesSelect
    if (is.null(species)) return(NULL)
    if (species == "") return(NULL)
    species <- gsub(' ', '_', species)
    files <- list.files(path=latest_dir, pattern=paste0("^", species, "_.*\\.snpDists.json"), full.names=TRUE, recursive=FALSE)
    list_of_nodes <- lapply(files, function(x) {
      node.json <- fromJSON(file = x)
      nodes <- as.data.frame(node.json[[2]])
      nodes$label <- ""
      nodes$id <- nodes$ID
      nodes$title <- nodes$ID
      nodes
    })

    species_nodes <- do.call(rbind,list_of_nodes)
    return(species_nodes)
  }

  get_edge_colours <- function(edges){
    print("function: get_edge_colours")
    if (is.null(edges)) {return(edges)}

    if (nrow(edges) == 0) {return(edges)}

    if (input$edgeColour == "Default"){
      edges$color <- '#848484'
    }

    if (input$edgeColour == "SNP Distance"){
      colfunc <- colorRampPalette(c("red", "blue"))
      edgeCols <- colfunc(input$distanceThreshold + 1)

      get_snp_col <- function(s1, s2, ...){
        SNP.mat <- values$SNP.mat
        s1 <- s1[['from']]
        s2 <- s2[['to']]

        dist <- SNP.mat[s1, s2]
        col <- edgeCols[dist + 1]
        return(col)
      }

      edges$color <- apply(edges, 1, function(x) get_snp_col(x['from'], x['to']))
    }

    if (input$edgeColour == "Delta Days"){
      get_delta_day <- function(s1, s2, ...){
        nodes <- values$nodes
        s1 <- s1[['from']]
        s2 <- s2[['to']]

        s1.date <- nodes[nodes$ID == s1, ]$date
        s2.date <- nodes[nodes$ID == s2, ]$date

        delta.days <- abs(s1.date-s2.date)

        return(delta.days)
      }

      edges$delta_days <- apply(edges, 1, function(x) get_delta_day(x['from'], x['to']))
      edges$delta_daysInt <- as.integer(edges$delta_days)

      colfunc <- colorRampPalette(c("red", "blue"))
      #edgeCols <- colfunc(max(edges$delta_daysInt) + 1)
      maxDays <- 365
      edgeCols <- colfunc(maxDays + 1)

      get_delta_day_col <- function(s1, ...){
        s1 <- as.integer(s1[['delta_daysInt']])
        if (s1 <= maxDays) {
          col <- edgeCols[s1 + 1]
        }
        else {
          col <- edgeCols[maxDays + 1]
        }

        return(col)
      }

      edges$color <- apply(edges, 1, function(x) get_delta_day_col(x['delta_daysInt']))
    }

    return(edges)
  }

  get_edges <- function(){
    print("function: get_edges")
    species <- input$speciesSelect
    st <- input$stSelect
    if (is.null(species) || is.null(st)) return(NULL)
    if (species == "" || st == "") return(NULL)
    species <- gsub(' ', '_', species)
    if (st == 'NA') st <- gsub('NA', 'ST_NA', st)
    path <- paste0(latest_dir, species, "_", st, ".snpDists")
    SNP.mat <- read.table(path, header = TRUE, check.names = FALSE)
    if (length(SNP.mat) == 1) SNP.mat <- read.csv(path, header = TRUE, check.names = FALSE, row.names=1)
    colnames(SNP.mat) <- gsub("-", "_", colnames(SNP.mat))
    rownames(SNP.mat) <- gsub("-", "_", rownames(SNP.mat))
    values$SNP.mat <- SNP.mat
    SNP.mat.ut <- upper.tri(SNP.mat)
    edges.all <- data.frame(
      from = rownames(SNP.mat)[row(SNP.mat)[SNP.mat.ut]],
      to = rownames(SNP.mat)[col(SNP.mat)[SNP.mat.ut]],
      SNPs = (SNP.mat)[SNP.mat.ut]
    )
    if (nrow(edges.all) > 0) edges.all$id <- 1:length(edges.all$from)
    edges.all <- get_edge_colours(edges.all)
    values$edges <- edges.all
    values$edges.all <- edges.all
    return(edges.all)
  }

  update_sts <- function(){
    nodes <- get_nodes()
    edges.all <- get_edges()
    if (is.null(nodes)) {
      print("Not updating!")
      return()
    }

    print("Updating!")
    values$species <- input$speciesSelect
    values$st <- input$stSelect

    edges <- edges.all[edges.all$SNPs <= input$distanceThreshold,]
    coords <- as.matrix(data.frame(x = nodes$Xn, y = nodes$Yn))

    values$edges <- edges

    output$cathai_plot <- renderVisNetwork({
      visNetwork(nodes, edges) %>%
        visNodes(fixed = TRUE, size = 5, label = NULL) %>%
        visEdges(smooth = FALSE) %>%
        visIgraphLayout(layout = "layout.norm", layoutMatrix = coords) %>%
        visOptions(highlightNearest = FALSE, autoResize = TRUE) %>%
        visPhysics(stabilization = FALSE) %>%
        visInteraction(dragNodes = FALSE, dragView = TRUE, zoomView = TRUE, selectable = TRUE, hover = FALSE, tooltipDelay = 0) %>%
        visExport(name = "CATHAI") %>%
        visEvents(selectNode = "function(e){
              Shiny.setInputValue('plot_baseNode', e.nodes[0]);
              }") %>%
        visEvents(deselectNode = "function(e){
                  Shiny.setInputValue('plot_baseNode', '');
                  }") %>%
        visEvents(click = "function(props){
              console.log(props);
              if (props.nodes.length == 0) {
                var el = document.getElementById('graphcathai_plot');
                var network = el.chart;
                network.selectEdges([]);
              }
              }")
    })

    updateSelectInput(session, 'baseNode', label = "Select Node:", choices = nodes$id, selected = "")
    updateSelectInput(session, 'selectNodes', label = "Show Node/s:", choices = nodes$id, selected = "")

    # Update clusters
    species <- input$speciesSelect
    st <- input$stSelect
    st <- gsub('ST', '', st)
    if (st == '_NA') st <- "NA"

    sST.clusters <- clusters[clusters$SPECIES == species & clusters$ST == st, ]
    values$sST.clusters <- sST.clusters
    updateSelectInput(session, 'selectCluster', label = "Select cluster:", choices = sST.clusters$CLUSTER, selected = "")
  }

  observeEvent(input$stSelect, ignoreNULL = FALSE, {
    print("obEvent: input$stSelect")
    update_sts()
  })

  get_sts <- function(){
    print("function: get_sts")
    species <- input$speciesSelect
    if (is.null(species)) species <- default_species
    return(sST.json[[species, exact = FALSE]])
  }

  filter_edges <- function(){
    print("function: filter_edges")
    edges.all <- values$edges.all
    edges <- edges.all[edges.all$SNPs <= input$distanceThreshold,]
    edges <- get_edge_colours(edges)
    return(edges)
  }

  gen_epi <- reactive({
    if (is.null(input$stSelect) || input$stSelect == "" || is.null(input$speciesSelect) || input$speciesSelect == ""){
      image <- load.image("cathai.png")
      return(image)
    }

    '%!in%' <- function(x,y)!('%in%'(x,y))

    if (input$stSelect %!in% get_sts()) {
      image <- load.image("cathai.png")
      return(image)
    }

    nodes <- get_nodes()

    if (length(nodes) <= 1) {
      image <- load.image("cathai.png")
      return(image)
    }

    cleaned_nodes <- nodes[ , -which(names(nodes) %in% c("text", "Xn", "Yn", "intDate", "label", "id", "title", "color"))]
    cleaned_nodes$Cluster <- apply(cleaned_nodes, 1, function(x) identify_cluster(x['ID']))

    cleaned_nodes$Cluster[cleaned_nodes$Cluster==""] <- "Unclassified"

    cleaned_nodes <- cleaned_nodes %>% group_by(`Cluster`)

    # Generate epidemic curve for all Clusters
    cases_byDate <- count(cleaned_nodes, `sample.date`, name = 'freq')
    create_colorPal_1 = colorRampPalette(brewer.pal(12, "Paired"))
    Cluster_color_all <- create_colorPal_1(length(unique(cases_byDate$`Cluster`)))
    cases_byDate$date <- as.Date(parsedate::parse_date(cases_byDate$sample.date))
    cases_byDate <- cases_byDate[!is.na(cases_byDate$date),]
    if (nrow(cases_byDate) <= 1) {
      image <- load.image("cathai.png")
      return(image)
    }

    epidemic_curve_allST <- EpiCurve(cases_byDate, date = "date",
                                     freq = "freq", period = "day",
                                     to.period = "week",
                                     cutvar = "Cluster",
                                     color= Cluster_color_all,
                                     ylabel= "Number of cases",
                                     xlabel= "Week of Year",
                                     title = "Epidemic curve of all Clusters (weekly)")
    x_labels <- epidemic_curve_allST$data$Date
    x_labels <- unique(x_labels)
    epidemic_curve_allST <- epidemic_curve_allST +
      scale_x_discrete(limits = x_labels, breaks = x_labels[seq(1,length(x_labels),by=3)])

    if (is.null(input$baseNode) || input$baseNode == "") {
      return(epidemic_curve_allST +
               theme(legend.position = "bottom", legend.key.size = unit(0.5,"line"))
      )
    } else {
      baseNode <- cleaned_nodes[cleaned_nodes$ID == input$baseNode,]

      return(epidemic_curve_allST +
               theme(legend.position = "bottom", legend.key.size = unit(0.5,"line")) +
               gghighlight(Date == ISOweek(baseNode$date), Cut == baseNode$Cluster,
                           use_direct_label = FALSE, unhighlighted_params = list(alpha = 0.3))
      )
    }
  })

  observeEvent(input$distanceThreshold, {
    print("obEvent: input$distanceThreshold")
    edges.current <- values$edges
    edges.new <- filter_edges()
    edges.rem <- setdiff(edges.current$id, edges.new$id)

    values$edges <- edges.new

    visNetworkProxy("cathai_plot") %>%
      visUpdateEdges(edges = edges.new) %>%
      visRemoveEdges(id = edges.rem)
  })

  observeEvent(input$plot_baseNode, {
    print("obEvent: input$plot_baseNode")
    if (is.null(input$baseNode) || input$plot_baseNode != input$baseNode) {
      updateSelectInput(session, 'baseNode', label = "Select Node:", choices = values$nodes$id, selected = input$plot_baseNode)
    }
  })

  set_labels <- function(nodes){
    print("function: set_labels")
    if (is.null(nodes)) {return(nodes)}

    SNP.mat <- values$SNP.mat
    labelBase <- input$baseNode

    if (is.null(labelBase) || labelBase == ""){
      nodes$title <- nodes$id
    }
    else {
      get_snp_distance <- function(s1, s2, ...){
        ret <- paste0(s2$ID, "<br>SNP Distance: ", SNP.mat[s1, s2$ID])
        return(ret)
      }

      nodes$title <- apply(nodes, 1, function(x) get_snp_distance(labelBase, x['ID']))
    }
    return(nodes)
  }

  observeEvent(input$baseNode, {
    print("obEvent: input$baseNode")

    labelBase <- values$labelBase
    if (is.null(labelBase) || input$baseNode != labelBase){
      nodes <- values$nodes
      nodes <- set_labels(nodes)

      visNetworkProxy("cathai_plot") %>%
        visUpdateNodes(nodes = nodes)

      values$nodes <- nodes
      values$labelBase <- input$baseNode
    }
    if (is.null(input$plot_baseNode) && input$baseNode == "") {
      return()
    }
    if (is.null(input$plot_baseNode) || input$plot_baseNode != input$baseNode) {
      if (input$baseNode != ""){
        visNetworkProxy("cathai_plot") %>%
          visSelectNodes(id = input$baseNode)
      }
    }
  })

  # URL parameter handling
  observe({
    print("ob: URL")
    query <- parseQueryString(session$clientData$url_search)
    if (!is.null(query[['snps']])) {
      updateSliderInput(session, "distanceThreshold", value = query[['snps']])
    }
  })

  #update ST options
  observeEvent(input$speciesSelect, {
    print("obEvent: input$speciesSelect")
    sts = get_sts()
    if (input$speciesSelect == default_species) {updateSelectInput(session, "stSelect", choices = sts, selected = default_st)}
    else {
      updateSelectInput(session, "stSelect", choices = sts, selected = NULL)
      if (values$st == sts[1]) {update_sts()}
    }
  })

  observeEvent(input$baseFocus, {
    print("obEvent: input$baseFocus")
    if (is.null(input$baseNode) || input$baseNode == "") {return()}
    visNetworkProxy("cathai_plot") %>%
      visFocus(id = input$baseNode, locked = FALSE)
  })

  observeEvent(input$baseClear, {
    print("obEvent: input$baseClear")
    if (is.null(input$baseNode) || input$baseNode == "") {return()}
    updateSelectInput(session, 'baseNode', label = "Select Node:", selected = "")
    visNetworkProxy("cathai_plot") %>%
      visUnselectAll()
  })

  observeEvent(input$selectNodes, {
    print("obEvent: input$selectNodes")
    nodes <- values$nodes
    nodes <- get_node_colours(nodes)

    visNetworkProxy("cathai_plot") %>%
      visUpdateNodes(nodes = nodes)

    values$nodes <- nodes
  })

  observeEvent(input$selectFocus, {
    print("obEvent: input$selectFocus")
    sel_nodes <- input$selectNodes
    if (is.null(input$selectNodes) || input$selectNodes == "") {sel_nodes <- NULL}
    base_node <- input$baseNode
    if (is.null(input$baseNode) || input$baseNode == "") {base_node <- NULL}
    com_nodes <- c(sel_nodes, base_node)
    visNetworkProxy("cathai_plot") %>%
      visFit(nodes = com_nodes)
  })

  observeEvent(input$selectClear, {
    print("obEvent: input$selectClear")
    updateSelectInput(session, 'selectNodes', label = "Select Node/s:", selected = "")
  })

  observeEvent(input$clusterFocus, {
    print("obEvent: input$clusterFocus")
    cluster <- input$selectCluster
    if (is.null(input$selectCluster) || input$selectCluster == "") {return()}

    species <- input$speciesSelect
    st <- input$stSelect
    if (is.null(species) || is.null(st)) return(NULL)
    if (species == "" || st == "") return(NULL)
    species <- gsub('_', ' ', species)
    st <- gsub('ST', '', st)
    if (st == '_NA') st <- "NA"

    sST.clusters <- clusters[clusters$SPECIES == species & clusters$ST == st, ]
    cluster_nodes <- sST.clusters[sST.clusters$CLUSTER == cluster, ]$MEMBERS[[1]]
    intersect_nodes <- intersect(cluster_nodes, values$nodes$id)

    visNetworkProxy("cathai_plot") %>%
      visFit(nodes = intersect_nodes)
  })

  observeEvent(input$clusterClear, {
    print("obEvent: input$clusterClear")
    if (is.null(input$selectCluster) || input$selectCluster == "") {return()}
    updateSelectInput(session, 'selectCluster', label = "Select Cluster:", selected = "")

  })

  observeEvent(input$selectCluster, {
    print("obEvent: input$selectCluster")
    nodes <- values$nodes
    nodes <- get_node_colours(nodes)

    visNetworkProxy("cathai_plot") %>%
      visUpdateNodes(nodes = nodes)

    values$nodes <- nodes
  })

  observeEvent(input$nodeColour, {
    print("obEvent: input$nodeColour")
    nodes <- values$nodes
    nodes <- get_node_colours(nodes)

    visNetworkProxy("cathai_plot") %>%
      visUpdateNodes(nodes = nodes)

    values$nodes <- nodes
  })

  observeEvent(input$edgeColour, {
    print("obEvent: input$edgeColour")
    edges <- values$edges
    edges <- get_edge_colours(edges)

    visNetworkProxy("cathai_plot") %>%
      visUpdateEdges(edges = edges)

    values$edges <- edges
  })

  observeEvent(input$resetZoom, {
    visNetworkProxy("cathai_plot") %>%
      visFit()
  })

  observeEvent(input$download_png, {
    print("Download")
    runjs('document.getElementById("downloadcathai_plot").click();')
  })

  get_filtered_nodes <- reactive({
    print("reactive: get_filtered_nodes")
    nodes <- values$nodes
    if (is.null(nodes)) {return(NULL)}
    cleaned_nodes <- nodes[ , -which(names(nodes) %in% c("text", "Xn", "Yn", "intDate", "label", "id", "title", "color", "date"))]

    cleaned_nodes$Cluster <- apply(cleaned_nodes, 1, function(x) identify_cluster(x['ID']))
    if ((is.null(input$baseNode) || input$baseNode == "") && (is.null(input$selectNodes) || input$selectNodes == "") && (is.null(input$selectCluster) || input$selectCluster == "")) {
      names(cleaned_nodes) <- str_to_title(str_squish(gsub("\\.", " ", names(cleaned_nodes))), locale = 'en')
      return(cleaned_nodes)
    }

    sel_nodes <- c(input$selectNodes, input$baseNode)

    if (!is.null(input$baseNode) && input$baseNode != ""){
      SNP.mat <- values$SNP.mat
      idx <- which(SNP.mat[input$baseNode, ] <= input$distanceThreshold, arr.ind=TRUE)
      thres_nodes <- rownames(SNP.mat)[idx[,"col"]]
      sel_nodes <- c(sel_nodes, thres_nodes)

      cleaned_nodes[[paste0('Distance From ', input$baseNode)]] <- apply(cleaned_nodes, 1, function(x) SNP.mat[input$baseNode, x['ID']])
    }

    if (!is.null(input$selectCluster) && input$selectCluster != "") {
      clust_nodes <- clusters[clusters$CLUSTER == input$selectCluster, ]$MEMBERS[[1]]
      sel_nodes <- c(sel_nodes, clust_nodes)
    }

    filtered_nodes <- cleaned_nodes[cleaned_nodes$ID %in% sel_nodes, ]
    names(filtered_nodes) <- str_to_title(str_squish(gsub("\\.", " ", names(filtered_nodes))), locale = 'en')
    return(filtered_nodes)
  })

  get_filtered_species_nodes <- reactive({
    print("reactive: get_filtered_nodes")
    nodes <- get_species_nodes()
    if (is.null(nodes)) {return(NULL)}
    cleaned_nodes <- nodes[ , -which(names(nodes) %in% c("text", "Xn", "Yn", "intDate", "label", "id", "title", "color", "date"))]

    cleaned_nodes$Cluster <- apply(cleaned_nodes, 1, function(x) identify_cluster(x['ID']))
    if ((is.null(input$baseNode) || input$baseNode == "") && (is.null(input$selectNodes) || input$selectNodes == "") && (is.null(input$selectCluster) || input$selectCluster == "")) {return(cleaned_nodes)}

    sel_nodes <- c(input$selectNodes, input$baseNode)

    if (!is.null(input$baseNode) && input$baseNode != ""){
      SNP.mat <- values$SNP.mat
      idx <- which(SNP.mat[input$baseNode, ] <= input$distanceThreshold, arr.ind=TRUE)
      thres_nodes <- rownames(SNP.mat)[idx[,"col"]]
      sel_nodes <- c(sel_nodes, thres_nodes)

      cleaned_nodes[[paste0('Distance From ', input$baseNode)]] <- apply(cleaned_nodes, 1, function(x) SNP.mat[input$baseNode, x['ID']])
    }

    if (!is.null(input$selectCluster) && input$selectCluster != "") {
      clust_nodes <- clusters[clusters$CLUSTER == input$selectCluster, ]$MEMBERS[[1]]
      sel_nodes <- c(sel_nodes, clust_nodes)
    }

    filtered_nodes <- cleaned_nodes[cleaned_nodes$ID %in% sel_nodes, ]
    return(filtered_nodes)
  })

  output$table <-  DT::renderDataTable({
    get_filtered_nodes()},
    server = FALSE,
    extensions = c('Buttons'),
    options = list(
      dom = 'Bfrtlip',
      orientation ='landscape',
      buttons = list('copy', 'csv', 'excel', list(extend = 'pdf', pageSize = 'A4', orientation = 'landscape', customize = JS("function (doc) {doc.defaultStyle.fontSize = 8;}"), filename ="CATHAI"), 'print'),
      lengthMenu = list(c(10, 25, 50, -1), c('10', '25', '50', 'All')),
      pageLength = 10,
      lengthChange = TRUE
    )
  )

  output$speciesTable <- DT::renderDataTable({
    get_filtered_species_nodes()},
    server = FALSE,
    extensions = c('Buttons'),
    options = list(
      dom = 'Bfrtlip',
      buttons = c('copy', 'csv', 'excel', 'pdf', 'print'),
      lengthMenu = list(c(10, 25, 50, -1), c('10', '25', '50', 'All')),
      pageLength = 10,
      lengthChange = TRUE
    )
  )

  output$epi_plot <- renderPlot(plot(tryCatch(gen_epi(), error = load.image("cathai.png")), height = 300))
  output$mobile_legend <- renderPlot(grid.draw(mobile_legend), height=22)
  output$legend <- renderPlot(grid.draw(legend), width=50)

}

