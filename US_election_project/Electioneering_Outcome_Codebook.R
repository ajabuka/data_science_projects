####### Setting Working Directory #######
# Change the working directory
setwd("C:/Users/ajaka/OneDrive - Teesside University/CIS4047 - Data Science Foundations/ICA - DSF")

# check current working directory
getwd()

# list the files in the working directory
list.files(getwd())

####### Importing Required Libraries and Reading Dataset #######
# Loading library
library(tidyverse)
library(DescTools)
library(RDCOMClient)
library(gridExtra)
library(scales)
library(class)
library(caret)
library(pROC)
library(car)

# Read the csv file
data <- read.csv("ElectionFinanceData.csv", na.strings=c("","NA"))

####### Data Preparation and Data Cleaning #######
# Get the column names of data
colnames(data)

head(data)

# Checking Data attributes
str(data)

# Checking for missing values
sum(is.na(data))

# Checking for proportion of missing data
pctmiss <- colSums(is.na(data))/nrow(data)
round(pctmiss, 2)

# Drop Columns not needed based on factors such as in already calculated columns
working_data <- select(data, can_off, can_off_sta, can_off_dis,
             can_par_aff, can_inc_cha_ope_sea, net_con,
             net_ope_exp, cov_sta_dat, cov_end_dat, winner)

# Checking Data attributes
str(working_data)

# Checking for missing values
sum(is.na(working_data))

# Checking for proportion of missing data
pctmiss <- colSums(is.na(working_data))/nrow(working_data)
round(pctmiss, 2)

# Explore the data for missing values
names(which(colSums(is.na(working_data)) > 0))

# remove rows with missing values
working_data <- working_data[!is.na(working_data$net_con), ]
working_data <- working_data[!is.na(working_data$net_ope_exp), ]
working_data <- working_data[!is.na(working_data$can_off_dis), ]
working_data <- working_data[!is.na(working_data$can_inc_cha_ope_sea), ]

# Renaming party affiliations because US runs a Two party System
working_data <- mutate(working_data,
                       can_par_aff = ifelse(can_par_aff %in% c("DEM", "REP"),
                                            can_par_aff, "OTHER"))

# Converting Date Columns to date data
working_data$cov_sta_dat <- parse_date_time(working_data$cov_sta_dat,
                                            orders = "mdy")

working_data$cov_end_dat <- parse_date_time(working_data$cov_end_dat,
                                            orders = "mdy")

# Creating New Calculated Columns
working_data$net_diff <- (working_data$net_con - working_data$net_ope_exp)
working_data$camp_days <- (working_data$cov_end_dat - working_data$cov_sta_dat)

# Drop date columns
working_data <- select(working_data, -cov_sta_dat, -cov_end_dat)

# Rename Columns
data.table::setnames(working_data, "can_inc_cha_ope_sea", "can_status")

####### Data Transformation and Summaries #######
# Creating list of Columns
categorical_columns <- c("can_off", "can_off_sta", "can_par_aff",
                         "can_status", "winner")

numeric_columns = c("net_con", "net_ope_exp", "net_diff", "camp_days")

# Converting Categorical Data to factors
working_data$can_off <- as.factor(working_data$can_off)
working_data$can_off_sta <- as.factor(working_data$can_off_sta)
working_data$can_par_aff <- as.factor(working_data$can_par_aff)
working_data$can_status <- as.factor(working_data$can_status)
working_data$winner <- as.factor(working_data$winner)

# Converting day difference to numeric
working_data$camp_days <- as.numeric(working_data$camp_days)


# Describing the Data
# Summaries of Categorical Columns
sum_cat_columns <- summary(working_data[categorical_columns])
sum_cat_columns

# Summaries of Numeric Columns and export to Word document
sum_num_columns <- do.call(cbind, lapply(working_data[numeric_columns], 
                                         summary)) %>%
  round(digit = 2) %>%
  format(scientific = FALSE)
sum_num_columns
ToWrd (sum_num_columns, wrd = GetNewWrd())

# Checking for proportion of winners by office and export to Word document
office_prop <- PercTable(winner ~ can_off, data = working_data, rfrq="111")
office_prop
ToWrd (office_prop, wrd = GetNewWrd())

# Filter Data Based on Candidate Office for some Visualizations
president_data = filter(working_data,
                     can_off == "P")

senate_data = filter(working_data,
                     can_off == "S")

house_data = filter(working_data,
                     can_off == "H")


####### Exploratory Data Analysis and Visualization #######

# Bar Plots to check Ratio
# Ratio of Election Outcomes by Party Affiliation
plot_can_par_aff = ggplot(working_data, aes(x = can_par_aff, fill = winner)) +
  geom_bar(position = "fill") +
  labs(title = "Candidate Party Affiliation by Election Outcome",
       fill = "Election Outcome",
       x = "Candidate Party Affiliation",
       y = "Outcome Ratio") +
  scale_x_discrete(labels  = c("DEM" = "DEMOCRAT", "REP" = "REPUBLICAN")) +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal() 

# Ratio of Election Outcomes by Candidate Election Status
plot_can_status = ggplot(working_data, aes(x = can_status, fill = winner)) +
  geom_bar(position = "fill") +
  labs(title = "Candidate Status Going to Election by Election Outcome",
       fill = "Election Outcome",
       x = "Candidate Election Status",
       y = "Outcome Ratio") +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()

# Grid Plots showing ratio
grid.arrange(
  plot_can_par_aff, plot_can_status, ncol = 2
)


# Bar Plots to compare Average of Categorical against Numerical Columns

# Bar Plots on Candidate Party Affiliation Averages
# Calculate and plot the average Net Contribution by Candidate Party Affiliation and Election Outcome
plot_can_par_con <- ggplot(working_data, aes(x = can_par_aff, y = net_con,
                                             fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  scale_y_continuous(labels = comma) +
  labs(title = "Avg Net Contribution by Party Affiliation and Election Outcome",
       x = "Candidate Party Affiliation",
       y = "Average Net Contribution",
       fill = "Election Outcome") +
  scale_x_discrete(labels  = c("DEM" = "DEMOCRAT", "REP" = "REPUBLICAN")) +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Calculate and plot the average Net Expenditure by Candidate Party Affiliation and Election Outcome
plot_can_par_exp <- ggplot(working_data, aes(x = can_par_aff, y = net_ope_exp,
                                             fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  scale_y_continuous(labels = comma) +
  labs(title = "Avg Net Expenditure by Party Affiliation and Election Outcome",
       x = "Candidate Party Affiliation",
       y = "Average Net Expenditure",
       fill = "Election Outcome") +
  scale_x_discrete(labels  = c("DEM" = "DEMOCRAT", "REP" = "REPUBLICAN")) +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Calculate and plot the Average Net Difference by Candidate Party Affiliation and Election Outcome
plot_can_par_diff <- ggplot(working_data, aes(x = can_par_aff, y = net_diff,
                                              fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  scale_y_continuous(labels = comma) +
  labs(title = "Avg Net Difference by Party Affiliation and Election Outcome",
       x = "Candidate Party Affiliation",
       y = "Average Net Difference",
       fill = "Election Outcome") +
  scale_x_discrete(labels  = c("DEM" = "DEMOCRAT", "REP" = "REPUBLICAN")) +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Calculate and plot the Average Campaign Days by Candidate Party Affiliation and Election Outcome
plot_can_par_days <- ggplot(working_data, aes(x = can_par_aff, y = camp_days,
                                              fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  labs(title = "Avg Campaign Days by Party Affiliation and Election Outcome",
       x = "Candidate Party Affiliation",
       y = "Average Campaign Days",
       fill = "Election Outcome") +
  scale_x_discrete(labels  = c("DEM" = "DEMOCRAT", "REP" = "REPUBLICAN")) +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Grid Plots show Averages based on Party Affiliation
grid.arrange(
  plot_can_par_con,
  plot_can_par_exp,
  plot_can_par_diff,
  plot_can_par_days,
  ncol = 2
)


# Bar Plots on Candidate Election Status (ES) Averages
# Calculate and plot the average Net Contribution by Candidate Election Status and Election Outcome
plot_can_ES_con <- ggplot(working_data, aes(x = can_status, y = net_con,
                                            fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  scale_y_continuous(labels = comma) +
  labs(title = "Avg Net Contribution by Election Status and Election Outcome",
       x = "Candidate Election Status",
       y = "Average Net Contribution",
       fill = "Election Outcome") +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Calculate and plot the average Net Expenditure by Candidate Election Status and Election Outcome
plot_can_ES_exp <- ggplot(working_data, aes(x = can_status, y = net_ope_exp,
                                            fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  scale_y_continuous(labels = comma) +
  labs(title = "Avg Net Expenditure by Election Status and Election Outcome",
       x = "Candidate Election Status",
       y = "Average Net Expenditure",
       fill = "Election Outcome") +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Calculate and plot the Average Net Difference by Candidate Election Status and Election Outcome
plot_can_ES_diff <- ggplot(working_data, aes(x = can_status, y = net_diff,
                                             fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  scale_y_continuous(labels = comma) +
  labs(title = "Avg Net Difference by Election Status and Election Outcome",
       x = "Candidate Election Status",
       y = "Average Net Difference",
       fill = "Election Outcome") +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Calculate and plot the Average Campaign Days by Candidate Election Status and Election Outcome
plot_can_ES_days <- ggplot(working_data, aes(x = can_status, y = camp_days,
                                             fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  labs(title = "Avg Campaign Days by Election Status and Election Outcome",
       x = "Candidate Election Status",
       y = "Average Campaign Days",
       fill = "Election Outcome") +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Grid Plots show Averages based on Election Status
grid.arrange(
  plot_can_ES_con,
  plot_can_ES_exp,
  plot_can_ES_diff,
  plot_can_ES_days,
  ncol = 2
)


# Bar Plots on Presidential Data
# Calculate and plot the average Net Contribution by Election Outcome
plot_pres_con <- ggplot(president_data, aes(x = winner, y = net_con,
                                            fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  scale_y_continuous(labels = comma) +
  labs(title = "Avg Net Contribution by Election Outcome for President",
       x = "Election Outcome",
       y = "Average Net Contribution",
       fill = "Election Outcome") +
  scale_x_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Calculate and plot the average Net Expenditure by Election Outcome
plot_pres_exp <- ggplot(president_data, aes(x = winner, y = net_ope_exp,
                                            fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  scale_y_continuous(labels = comma) +
  labs(title = "Avg Net Expenditure by Election Outcome for President",
       x = "Election Outcome",
       y = "Average Net Expenditure",
       fill = "Election Outcome") +
  scale_x_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Calculate and plot the Average Net Difference by Election Outcome
plot_pres_diff <- ggplot(president_data, aes(x = winner, y = net_diff,
                                             fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  scale_y_continuous(labels = comma) +
  labs(title = "Avg Net Difference by Election Outcome for President",
       x = "Election Outcome",
       y = "Average Net Difference",
       fill = "Election Outcome") +
  scale_x_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Calculate and plot the Average Campaign Days by Election Outcome
plot_pres_days <- ggplot(president_data, aes(x = winner, y = camp_days,
                                             fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  labs(title = "Avg Campaign Days by Election Outcome for President",
       x = "Election Outcome",
       y = "Average Campaign Days",
       fill = "Election Outcome") +
  scale_x_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Grid Plots show Averages based on President
grid.arrange(
  plot_pres_con,
  plot_pres_exp,
  plot_pres_diff,
  plot_pres_days,
  ncol = 2
)


# Bar Plots on Senatorial Data
# Calculate and plot the average Net Contribution by Election Outcome
plot_sen_con <- ggplot(senate_data, aes(x = winner, y = net_con,
                                        fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  scale_y_continuous(labels = comma) +
  labs(title = "Avg Net Contribution by Election Outcome for Senate",
       x = "Election Outcome",
       y = "Average Net Contribution",
       fill = "Election Outcome") +
  scale_x_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Calculate and plot the average Net Expenditure by Election Outcome
plot_sen_exp <- ggplot(senate_data, aes(x = winner, y = net_ope_exp,
                                            fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  scale_y_continuous(labels = comma) +
  labs(title = "Avg Net Expenditure by Election Outcome for Senate",
       x = "Election Outcome",
       y = "Average Net Expenditure",
       fill = "Election Outcome") +
  scale_x_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Calculate and plot the Average Net Difference by Election Outcome
plot_sen_diff <- ggplot(senate_data, aes(x = winner, y = net_diff,
                                             fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  scale_y_continuous(labels = comma) +
  labs(title = "Avg Net Difference by Election Outcome for Senate",
       x = "Election Outcome",
       y = "Average Net Difference",
       fill = "Election Outcome") +
  scale_x_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Calculate and plot the Average Campaign Days by Election Outcome
plot_sen_days <- ggplot(senate_data, aes(x = winner, y = camp_days,
                                             fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  labs(title = "Avg Campaign Days by Election Outcome for Senate",
       x = "Election Outcome",
       y = "Average Campaign Days",
       fill = "Election Outcome") +
  scale_x_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Grid Plots show Averages based on Senate Elections
grid.arrange(
  plot_sen_con,
  plot_sen_exp,
  plot_sen_diff,
  plot_sen_days,
  ncol = 2
)


# Bar Plots on Candidate Party Affiliation Averages in Senate Elections
# Calculate and plot the average Net Contribution by Candidate Party Affiliation and Election Outcome
plot_sen_can_par_con <- ggplot(senate_data, aes(x = can_par_aff, y = net_con,
                                             fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  scale_y_continuous(labels = comma) +
  labs(title = "Senate Avg Net Contribution by Party Affiliation and Election Outcome",
       x = "Candidate Party Affiliation",
       y = "Average Net Contribution",
       fill = "Election Outcome") +
  scale_x_discrete(labels  = c("DEM" = "DEMOCRAT", "REP" = "REPUBLICAN")) +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Calculate and plot the average Net Expenditure by Candidate Party Affiliation and Election Outcome
plot_sen_can_par_exp <- ggplot(senate_data, aes(x = can_par_aff, y = net_ope_exp,
                                                fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  scale_y_continuous(labels = comma) +
  labs(title = "Senate Avg Net Expenditure by Party Affiliation and Election Outcome",
       x = "Candidate Party Affiliation",
       y = "Average Net Expenditure",
       fill = "Election Outcome") +
  scale_x_discrete(labels  = c("DEM" = "DEMOCRAT", "REP" = "REPUBLICAN")) +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Calculate and plot the Average Net Difference by Candidate Party Affiliation and Election Outcome
plot_sen_can_par_diff <- ggplot(senate_data, aes(x = can_par_aff, y = net_diff,
                                              fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  scale_y_continuous(labels = comma) +
  labs(title = "Senate Avg Net Difference by Party Affiliation and Election Outcome",
       x = "Candidate Party Affiliation",
       y = "Average Net Difference",
       fill = "Election Outcome") +
  scale_x_discrete(labels  = c("DEM" = "DEMOCRAT", "REP" = "REPUBLICAN")) +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Calculate and plot the Average Campaign Days by Candidate Party Affiliation and Election Outcome
plot_sen_can_par_days <- ggplot(senate_data, aes(x = can_par_aff, y = camp_days,
                                              fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  labs(title = "Senate Avg Campaign Days by Party Affiliation and Election Outcome",
       x = "Candidate Party Affiliation",
       y = "Average Campaign Days",
       fill = "Election Outcome") +
  scale_x_discrete(labels  = c("DEM" = "DEMOCRAT", "REP" = "REPUBLICAN")) +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Grid Plots show Averages based on Party Affiliation
grid.arrange(
  plot_sen_can_par_con,
  plot_sen_can_par_exp,
  plot_sen_can_par_diff,
  plot_sen_can_par_days,
  ncol = 2
)


# Bar Plots on Candidate Election Status (ES) Averages in Senate Elections
# Calculate and plot the average Net Contribution by Candidate Election Status and Election Outcome
plot_sen_can_ES_con <- ggplot(senate_data, aes(x = can_status, y = net_con,
                                            fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  scale_y_continuous(labels = comma) +
  labs(title = "Senate Avg Net Contribution by Election Status and Election Outcome",
       x = "Candidate Election Status",
       y = "Average Net Contribution",
       fill = "Election Outcome") +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Calculate and plot the average Net Expenditure by Candidate Election Status and Election Outcome
plot_sen_can_ES_exp <- ggplot(senate_data, aes(x = can_status, y = net_ope_exp,
                                            fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  scale_y_continuous(labels = comma) +
  labs(title = "Senate Avg Net Expenditure by Election Status and Election Outcome",
       x = "Candidate Election Status",
       y = "Average Net Expenditure",
       fill = "Election Outcome") +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Calculate and plot the Average Net Difference by Candidate Election Status and Election Outcome
plot_sen_can_ES_diff <- ggplot(senate_data, aes(x = can_status, y = net_diff,
                                             fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  scale_y_continuous(labels = comma) +
  labs(title = "Senate Avg Net Difference by Election Status and Election Outcome",
       x = "Candidate Election Status",
       y = "Average Net Difference",
       fill = "Election Outcome") +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Calculate and plot the Average Campaign Days by Candidate Election Status and Election Outcome
plot_sen_can_ES_days <- ggplot(senate_data, aes(x = can_status, y = camp_days,
                                             fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  labs(title = "Senate Avg Campaign Days by Election Status and Election Outcome",
       x = "Candidate Election Status",
       y = "Average Campaign Days",
       fill = "Election Outcome") +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Grid Plots show Averages based on Election Status
grid.arrange(
  plot_sen_can_ES_con,
  plot_sen_can_ES_exp,
  plot_sen_can_ES_diff,
  plot_sen_can_ES_days,
  ncol = 2
)


# Bar Plots on House Data
# Calculate and plot the average Net Contribution by Election Outcome
plot_house_con <- ggplot(house_data, aes(x = winner, y = net_con,
                                        fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  scale_y_continuous(labels = comma) +
  labs(title = "Avg Net Contribution by Election Outcome for House",
       x = "Election Outcome",
       y = "Average Net Contribution",
       fill = "Election Outcome") +
  scale_x_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Calculate and plot the average Net Expenditure by Election Outcome
plot_house_exp <- ggplot(house_data, aes(x = winner, y = net_ope_exp,
                                        fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  scale_y_continuous(labels = comma) +
  labs(title = "Avg Net Expenditure by Election Outcome for House",
       x = "Election Outcome",
       y = "Average Net Expenditure",
       fill = "Election Outcome") +
  scale_x_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Calculate and plot the Average Net Difference by Election Outcome
plot_house_diff <- ggplot(house_data, aes(x = winner, y = net_diff,
                                         fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  scale_y_continuous(labels = comma) +
  labs(title = "Avg Net Difference by Election Outcome for House",
       x = "Election Outcome",
       y = "Average Net Difference",
       fill = "Election Outcome") +
  scale_x_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Calculate and plot the Average Campaign Days by Election Outcome
plot_house_days <- ggplot(house_data, aes(x = winner, y = camp_days,
                                         fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  labs(title = "Avg Campaign Days by Election Outcome for House",
       x = "Election Outcome",
       y = "Average Campaign Days",
       fill = "Election Outcome") +
  scale_x_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Grid Plots show Averages based on House Elections
grid.arrange(
  plot_house_con,
  plot_house_exp,
  plot_house_diff,
  plot_house_days,
  ncol = 2
)


# Bar Plots on Candidate Party Affiliation Averages in House Elections
# Calculate and plot the average Net Contribution by Candidate Party Affiliation and Election Outcome
plot_house_can_par_con <- ggplot(house_data, aes(x = can_par_aff, y = net_con,
                                                fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  scale_y_continuous(labels = comma) +
  labs(title = "House Avg Net Contribution by Party Affiliation and Election Outcome",
       x = "Candidate Party Affiliation",
       y = "Average Net Contribution",
       fill = "Election Outcome") +
  scale_x_discrete(labels  = c("DEM" = "DEMOCRAT", "REP" = "REPUBLICAN")) +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Calculate and plot the average Net Expenditure by Candidate Party Affiliation and Election Outcome
plot_house_can_par_exp <- ggplot(house_data, aes(x = can_par_aff, y = net_ope_exp,
                                                fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  scale_y_continuous(labels = comma) +
  labs(title = "House Avg Net Expenditure by Party Affiliation and Election Outcome",
       x = "Candidate Party Affiliation",
       y = "Average Net Expenditure",
       fill = "Election Outcome") +
  scale_x_discrete(labels  = c("DEM" = "DEMOCRAT", "REP" = "REPUBLICAN")) +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Calculate and plot the Average Net Difference by Candidate Party Affiliation and Election Outcome
plot_house_can_par_diff <- ggplot(house_data, aes(x = can_par_aff, y = net_diff,
                                                 fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  scale_y_continuous(labels = comma) +
  labs(title = "House Avg Net Difference by Party Affiliation and Election Outcome",
       x = "Candidate Party Affiliation",
       y = "Average Net Difference",
       fill = "Election Outcome") +
  scale_x_discrete(labels  = c("DEM" = "DEMOCRAT", "REP" = "REPUBLICAN")) +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Calculate and plot the Average Campaign Days by Candidate Party Affiliation and Election Outcome
plot_house_can_par_days <- ggplot(house_data, aes(x = can_par_aff, y = camp_days,
                                                 fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  labs(title = "House Avg Campaign Days by Party Affiliation and Election Outcome",
       x = "Candidate Party Affiliation",
       y = "Average Campaign Days",
       fill = "Election Outcome") +
  scale_x_discrete(labels  = c("DEM" = "DEMOCRAT", "REP" = "REPUBLICAN")) +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Grid Plots show Averages based on Party Affiliation
grid.arrange(
  plot_house_can_par_con,
  plot_house_can_par_exp,
  plot_house_can_par_diff,
  plot_house_can_par_days,
  ncol = 2
)


# Bar Plots on Candidate Election Status (ES) Averages in House Elections
# Calculate and plot the average Net Contribution by Candidate Election Status and Election Outcome
plot_house_can_ES_con <- ggplot(house_data, aes(x = can_status, y = net_con,
                                               fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  scale_y_continuous(labels = comma) +
  labs(title = "House Avg Net Contribution by Election Status and Election Outcome",
       x = "Candidate Election Status",
       y = "Average Net Contribution",
       fill = "Election Outcome") +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Calculate and plot the average Net Expenditure by Candidate Election Status and Election Outcome
plot_house_can_ES_exp <- ggplot(house_data, aes(x = can_status, y = net_ope_exp,
                                               fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  scale_y_continuous(labels = comma) +
  labs(title = "House Avg Net Expenditure by Election Status and Election Outcome",
       x = "Candidate Election Status",
       y = "Average Net Expenditure",
       fill = "Election Outcome") +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Calculate and plot the Average Net Difference by Candidate Election Status and Election Outcome
plot_house_can_ES_diff <- ggplot(house_data, aes(x = can_status, y = net_diff,
                                                fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  scale_y_continuous(labels = comma) +
  labs(title = "House Avg Net Difference by Election Status and Election Outcome",
       x = "Candidate Election Status",
       y = "Average Net Difference",
       fill = "Election Outcome") +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Calculate and plot the Average Campaign Days by Candidate Election Status and Election Outcome
plot_house_can_ES_days <- ggplot(house_data, aes(x = can_status, y = camp_days,
                                                fill = winner)) +
  stat_summary(fun = "mean", geom = "bar", position = "dodge") +
  labs(title = "House Avg Campaign Days by Election Status and Election Outcome",
       x = "Candidate Election Status",
       y = "Average Campaign Days",
       fill = "Election Outcome") +
  scale_fill_discrete(labels  = c("Y" = "ELECTED", "N" = "LOST")) +
  theme_minimal()


# Grid Plots show Averages based on Election Status
grid.arrange(
  plot_house_can_ES_con,
  plot_house_can_ES_exp,
  plot_house_can_ES_diff,
  plot_house_can_ES_days,
  ncol = 2
)


####### Data Preprocessing #######
# Checking for Outlier using Z score to determining point 3-steps away
scaled_numeric_columns <- working_data %>% select_if(is.numeric)
scaled_numeric_columns <- select(scaled_numeric_columns, -can_off_dis)
scaled_numeric_columns <- scale(scaled_numeric_columns)
outlier_now <- apply(scaled_numeric_columns, 2, function(x) which(abs(x) > 3.29))

# Visualise Outliers in a table
outliers <- working_data[outlier_now$net_ope_exp, ]
outliers
ToWrd(outliers, wrd = GetNewWrd())


# Checking for the proportion of the dataset 
data_prop <- working_data %>%
  group_by(winner) %>%
  summarise(count = n()) %>%
  mutate(props = round(count / sum(count), 2))
data_prop
ToWrd(data_prop, wrd = GetNewWrd())

# Encoding Categorical Variables
working_data = working_data %>% 
  mutate(
    can_off = as.numeric(factor(can_off)),
    can_off_sta = as.numeric(factor(can_off_sta)),
    can_par_aff = as.numeric(factor(can_par_aff)),
    can_status = as.numeric(factor(can_status)),
    winner = as.numeric(factor(winner, levels = c("Y", "N"))) - 1 
  )

# Standardizing Feature Columns
working_data <- working_data %>% 
  mutate(
    can_off = scale(can_off),
    can_off_sta = scale(can_off_sta),
    can_off_dis = scale(can_off_dis),
    can_par_aff = scale(can_par_aff),
    can_status = scale(can_status),
    net_con = scale(net_con),
    net_ope_exp = scale(net_ope_exp),
    net_diff = scale(net_diff),
    camp_days = scale(camp_days)
  )

# Checking for Correlation and MultiCollinearity in Features
# Checking for Correlation
corrmatrix <- cor(select(working_data, -winner))
corrplot::corrplot(corrmatrix, method = "number")

# Printing highly correlated Features
highly_corr <- alias(glm(winner ~ ., data = working_data, family = binomial))
highly_corr
ToWrd(highly_corr, wrd = GetNewWrd())

# dropping net_con and net_diff
model_data <- select(working_data, -net_con, -net_diff)

# Checking for MultiCollinearity using VIF
model_data_glm <- glm(winner ~ ., data = model_data, family = binomial)
model_data_vif <- vif(model_data_glm)
model_data_vif
ToWrd(model_data_vif, wrd = GetNewWrd())

####### Model Building and Testing #######
# Checking for missing values
anyNA(model_data)

# factor target
model_data$winner <- as.factor(model_data$winner)

# Splitting Data into Training and Testing Set
set.seed(42)
train_index <- createDataPartition(model_data$winner, p = 0.8, list = FALSE)
train_data <- model_data[train_index, ]
test_data <- model_data[-train_index, ]

# Separate features
# Separate train features and labels
train_feature <- train_data %>% select(-winner)
train_label <- train_data$winner

# Separate test features and labels
test_features <- test_data %>% select(-winner)
test_labels <- test_data$winner

# checking training and testing datasets dimensions
dim(train_feature)
dim(test_features)


# Finding the optimum K value
# set k values
values_k <- c(3, 5, 7)

# set a list to store k values
results <- list()

# iterating over k values and getting results
for (k in values_k){
  knn_model <- knn(train = train_feature, test = test_features, cl = train_label, k = k)
  results[[paste0("k = ", k)]] <- confusionMatrix(knn_model, test_labels)
}

results

# Train and Save Model with Best performing k
k <- 5
start_time <- Sys.time() # Record start time for model
knn_model <- knn(train = train_feature, test = test_features, cl = train_label, k = k)
stop_time <- Sys.time() # Record model ending time

training_time <- stop_time - start_time # Calculate training time

# Save Model
saveRDS(knn_model, file = "Election_Finance_Model.rds")

# Assessing Model Performance with Confusion Matrix
model_conf_matrix <- confusionMatrix(knn_model, test_labels)

# Printing Time Taken and Confusion Matrix
cat("Training Time: ", training_time, "\n")
model_conf_matrix

# Plotting the confusion Matrix
model_conf_mat_data = as.data.frame(model_conf_matrix$table)
model_conf_matrix_plot <- model_conf_mat_data %>%
  ggplot(aes(x = Prediction, y = Reference, fill = Freq)) +
  geom_tile() +
  geom_text(aes(label = Freq))
model_conf_matrix_plot


# Plot ROC Curve
test_labels_binary <- as.numeric(test_labels) - 1
knn_model_binary <- as.numeric(knn_model) - 1

# Compute the ROC Curve and AUC
roc_curve <- roc(test_labels_binary, knn_model_binary)
plot(roc_curve, col = "blue", main = "ROC Curve for KNN Model", lwd = 2)
auc_value <- auc(roc_curve)
text(0.6, 0.4, paste("AUC =", round(auc_value, 2)), col = "red")
