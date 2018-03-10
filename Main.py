import datetime
import pandas as pd
import Veil_Darkness as veil
import Address_Analysis as addy
import Convert_Filter as filt
import Bootstrap_Analysis as boot

##### Import and filtering #####

# Read in original CSV citations
filename = "FerndaleCitations2009_2017"
# filename = "FerndaleCitationsSample"
filetype = ".csv"

parseDates = ['CITATION_DT','FORM_CITATION_DT']

## Read csv into pandas dataframe
# rawData = pd.read_csv(filename + filetype, parse_dates=parseDates, header=0, low_memory=False)
# rawData.to_pickle(filename + ".pkl")
## Read pickle instead of csv to speed up processing
rawData = pd.read_pickle(filename + ".pkl")
citations = pd.DataFrame(rawData)

## Do filtering on one year and export to csv
filterYear = 2012
citations, citationsResults = filt.filterData(citations, filterYear)
citations.to_csv(filename + "_filtered" + filetype)

## Run Bootstrap analysis
bootstrapResults = boot.runBootstrap(citations)

## Run Veil of Darkness analysis
# returnVeil = veil.runVeil(citations, filename)

## Write Veil of Darkness results to file for one year
# columnsList = ['PARK_VIOL_EXCL', 'RACE_EXCL','RACE_B','RACE_W','RACE_A','RACE_U','RACE_I','BLANK_EXCL','MI_EXCL','DATE_EXCL','TOTAL_EXCL','TOTAL_FILT','EARLY_SUNSET','LATE_SUNSET','ODDS_RATIO','DAY_VEIL_P','DAY_VEIL_STDERROR','BLACK_CNT_DAY','BLACK_CNT_NIGHT','TOTAL_DAY','TOTAL_NIGHT','BLACK_PCT_DAY','BLACK_PCT_NIGHT','TWO_SAMPLE_DIFF']
#
# citationsResults.extend(returnVeil)
# resultsDF = pd.DataFrame()
# resultsDF = resultsDF.append([citationsResults])
# resultsDF.columns = columnsList
# resultsDF.to_csv(filename + "_Results" + filetype)

## Write Veil of Darkness results to file for multiple years
# years=[2009,2010,2011,2012,2013,2014,2015,2016,2017]
# resultsDF = pd.DataFrame()
#
# for year in years:
#     citations = pd.DataFrame(rawData)
#     citations, citationsResults = filt.filterData(citations, year)
#     returnVeil = veil.runVeil(citations, filename)
#     citationsResults.extend(returnVeil)
#     citationsResults.extend([year])
#     resultsDF = resultsDF.append([citationsResults])
#
# columnsList = ['PARK_VIOL_EXCL', 'RACE_EXCL','RACE_B','RACE_W','RACE_A','RACE_U','RACE_I','BLANK_EXCL','MI_EXCL','DATE_EXCL','TOTAL_EXCL','TOTAL_FILT','EARLY_SUNSET','LATE_SUNSET','ODDS_RATIO','DAY_VEIL_P','DAY_VEIL_STDERROR','BLACK_CNT_DAY','BLACK_CNT_NIGHT','TOTAL_DAY','TOTAL_NIGHT','BLACK_PCT_DAY','BLACK_PCT_NIGHT','TWO_SAMPLE_DIFF',"YEAR"]
# resultsDF.columns = columnsList
# resultsDF.to_csv(filename + "_Results" + filetype)

## Run Address Analysis
# returnAddy = addy.runAddress(citations, filename)
## Get weighted averages
# print("Weighted average Black percent for citations: ")
# print((returnAddy["BLACK_PCT_CITATIONS"] * returnAddy["COUNT"]).sum() / returnAddy["COUNT"].sum())
# print("Weighted average Black percent for census: ")
# print((returnAddy["BLACK_PCT_CENSUS"] * returnAddy["HC01_VC03"]).sum() / returnAddy["HC01_VC03"].sum())
# print("Weighted average Black percent for census weighted by citations: ")
# print((returnAddy["BLACK_PCT_CENSUS"] * returnAddy["COUNT"]).sum() / returnAddy["COUNT"].sum())
# returnAddy.to_csv("addy_result" + str(filterYear) + ".csv")

## Get Address Analysis percent black for each year
# years=[2009,2010,2011,2012,2013,2014,2015,2016,2017]
# resultsDF = pd.DataFrame()
# racePctYear = []
#
# for year in years:
#     citations = pd.DataFrame(rawData)
#     citations, citationsResults = filt.filterData(citations, year)
#
#     raceCount = citations["OFF_RACE_CD"].value_counts()
#     returnAddy = addy.runAddress(citations, filename)
#     addyResults = []
#     addyResults.extend([year])
#     addyResults.extend([raceCount["B"]/citations.shape[0]])
#     addyResults.extend([(returnAddy["BLACK_PCT_CITATIONS"] * returnAddy["COUNT"]).sum() / returnAddy["COUNT"].sum()])
#     addyResults.extend([(returnAddy["BLACK_PCT_CENSUS"] * returnAddy["HC01_VC03"]).sum() / returnAddy["HC01_VC03"].sum()])
#     addyResults.extend([(returnAddy["BLACK_PCT_CENSUS"] * returnAddy["COUNT"]).sum() / returnAddy["COUNT"].sum()])
#     addyResults.extend([addyResults[2]-addyResults[4]])
#     resultsDF = resultsDF.append([addyResults])
#
# columnsList = ['YEAR','BLACK_PCT','WEIGHT_BLACK_PCT_CITATIONS','WEIGHT_BLACK_PCT_CENSUS','WEIGHT_BLACK_PCT_CENSUS_BY_CITATION','PCT_DIFF']
# resultsDF.columns = columnsList
# resultsDF.to_csv("addy_Results" + filetype)
#
# print(racePctYear)
