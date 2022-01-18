# Misc setup
useShinyjs(rmd = TRUE)

# Dashboard UI
ui <- fluidPage(
  tags$head(
    tags$link(rel = "stylesheet", type = "text/css", href = "styles.css"),
    tags$script(src = 'cathai.js')
  ),
  dashboardPage(
    title = "CATHAI",
    dashboardHeader(
      title = "CATHAI",
      tags$li(id = 'plot-nav', class = "dropdown header-tab active",
        tags$a(href="#", tags$p(class ="navTab", 'Plot'))
      ),
      tags$li(id = 'table-nav', class = "dropdown header-tab",
              tags$a(href="#", tags$p(class ="navTab", 'Table'))
      ),
      tags$li(id = 'species-nav', class = "dropdown header-tab",
              tags$a(href="#", tags$p(class ="navTab", 'Species Table'))
      ),
      tags$li(id = 'return-nav', class = "dropdown header-tab",
              tags$a(href=return_url, tags$p(class ="navTab", 'Exit'))
      )
    ),
    dashboardSidebar(
      div(style = "display: none !important",
        sidebarMenu(
          menuItem("Plot", tabName = "plot", selected = TRUE),
          menuItem("Table", tabName = "table"),
          menuItem("Species", tabName = "species")
        )
      ),
      # Species select
      selectInput("speciesSelect", "Species:", sort(names(sST.json)), selected = default_species),

      # ST select
      selectInput("stSelect", "ST:", choices = NULL),

      # SNP distance
      sliderInput("distanceThreshold", "SNP Distance Threshold:", min = 0, max = 100, value = 25, step = 1),

      # Base node
      selectizeInput("baseNode", "Select Node:", choices = c(''), multiple = FALSE, options = list(placeholder = 'Select node')),
      div(class = "cat-btn-grp",
        actionButton("baseFocus", "Focus", class = "left-button-sb"),
        actionButton("baseClear", "Clear", class = "right-button-sb"),
      ),

      # Highlight node/s
      selectizeInput("selectNodes", "Show Node/s:", choices = c(''), multiple = TRUE, options = list(placeholder = 'Select node/s', plugins = list("drag_drop", "remove_button"))),
      div(class = "cat-btn-grp",
          actionButton("selectFocus", "Focus", class = "left-button-sb"),
          actionButton("selectClear", "Clear", class = "right-button-sb"),
      ),

      # Select Cluster
      selectizeInput("selectCluster", "Select Cluster:", choices = c(''), multiple = FALSE, options = list(placeholder = 'Select Cluster')),
      div(class = "cat-btn-grp",
          actionButton("clusterFocus", "Focus", class = "left-button-sb"),
          actionButton("clusterClear", "Clear", class = "right-button-sb"),
      ),

      # Select Colour by Node
      selectizeInput("nodeColour", "Node Colouration:", choices = node_colour_choices, multiple = FALSE, selected = "Default"),
      selectizeInput("edgeColour", "Edge Colouration:", choices = edge_colour_choices, multiple = FALSE, selected = "Default"),

      div(class = "cat-btn-grp",
          actionButton("resetZoom", "Reset", class = "left-button-sb"),
          actionButton("download_png", "Save PNG", class = "right-button-sb"),
      ),
      div(id = "mobileTest")
    ),
    dashboardBody(
      tabItems(
        tabItem(tabName = 'plot',
          fillPage(
            tags$style(type = "text/css", "#plotContent {height: calc(100vh - 82px) !important;}"),
            div(id = "plotContent", style = "background-color: white !important; padding: 20px !important",
              fillCol(
                plotOutput('epi_plot', height = '300px', width = '100%'),
                fillRow(
                  fillCol(
                    plotOutput('mobile_legend', height = '12px'),
                    visNetworkOutput("cathai_plot", height = '100%'),
                    flex = c(NA, 1)
                  ),
                  div(style = "float: right; width: 50px",
                      plotOutput('legend')
                  ),
                  flex = c(1, NA)
                ),
                flex =c(NA, 1)
              )
            )
          )
        ),
        tabItem(tabName = 'table',
          fluidPage(
            div(id = "tableContent",
              fluidRow(
                dataTableOutput('table')
              )
            )
          )
        ),
        tabItem(tabName = 'species',
          fluidPage(
            div(id = "speciesContent",
              fluidRow(
                dataTableOutput('speciesTable')
              )
            )
          )
        )
      )
    )
  )
)
