import datetime
import pandas as pd
import numpy as np
import statsmodels.api as sm
import Veil_Darkness as veil
import Address_Analysis as addy
import Convert_Filter as filt
import Bootstrap_Analysis as boot

##### Import and filtering #####

## Read in original CSV citations
filename = "CitationsQuery2_complete"
filetype = ".csv"

## Old datefields: parseDates = ['CITATION_DT','FORM_CITATION_DT']
parseDates = ['Citation Date_x','Created Date_x']

## Read csv into pandas dataframe - parsing dates takes time, so pickeling for speedup
try:
    rawData = pd.read_pickle(filename + ".pkl")
except (OSError, IOError) as e:
    rawData = pd.read_csv(filename + filetype, parse_dates=parseDates, header=0, low_memory=False)
    rawData.to_pickle(filename + ".pkl")

citations = pd.DataFrame(rawData)
## Deal with ambiguous 2-digit dates and '69 date epoch
citations['BD_DATE']= citations['Offender Date of Birth'].str.split(' ').str[0]
citations['BD_DATE']= pd.to_datetime(citations['BD_DATE'], format="%m/%d/%y")
citations['BD_DATE']= citations['BD_DATE'].apply(lambda row: datetime.datetime(row.year - 100,row.month,row.day,0,0) if row.year > 2001 else row)

# ### Do filtering and export to csv
def filterResults(years):
    for year in years:
        citations = pd.DataFrame(rawData)
        citations, citationsResults = filt.filterData(citations, year[0], year[1], gender="All", age=(0,99))
        citations.to_csv(filename + "_filtered" + year[0] +"_"+ year[1] + filetype)

## Run Bootstrap analysis
def bootstrapAnalysis():
    citations, citationsResults = filt.filterData(citations, 2011, 2017)
    bootstrapResults = boot.runBootstrap(citations)

## Write Veil of Darkness results to file for each year & all years
def veilAnalysis(years):
    resultsDF = pd.DataFrame()

    for year in years:
        citations = pd.DataFrame(rawData)
        citations, citationsResults = filt.filterData(citations, year[0], year[1], gender=gender, age=age)
        returnVeil = veil.runVeil(citations, filename)
        citationsResults.extend(returnVeil)
        citationsResults.extend([year])
        resultsDF = resultsDF.append([citationsResults])

    columnsList = ['PARK_VIOL_EXCL', 'RACE_EXCL','RACE_B','RACE_W','RACE_A','RACE_U','RACE_I','BLANK_EXCL','MI_EXCL','DATE_EXCL','TOTAL_EXCL','TOTAL_FILT','EARLY_SUNSET','LATE_SUNSET','ODDS_RATIO','DAY_VEIL_P','DAY_VEIL_STDERROR','BLACK_CNT_DAY','BLACK_CNT_NIGHT','TOTAL_DAY','TOTAL_NIGHT','BLACK_PCT_DAY','BLACK_PCT_NIGHT','TWO_SAMPLE_DIFF',"YEAR"]
    resultsDF.columns = columnsList
    resultsDF.to_csv(filename + "_VoD_Results" + filetype)

## Get Address Analysis percent black for each year & all years
def censusBenchmark(years):
    resultsDF = pd.DataFrame()
    racePctYear = []

    for year in years:
        citations = pd.DataFrame(rawData)
        citations, citationsResults = filt.filterData(citations, year[0], year[1], gender=gender, age=age)

        raceCount = citations["Offender Race"].value_counts()
        returnAddy = addy.runAddress(citations, gender=gender, age=ageCategory)
        addyResults = []
        addyResults.extend([year])
        ## Total black drivers divided by total citations
        addyResults.extend([returnAddy["SUM"].sum() / returnAddy["COUNT"].sum()])
        ## Total black people (census) divided by total population (census)
        addyResults.extend([returnAddy["BLACK_POP_VEH_CENSUS"].sum() / returnAddy["TOTAL_POP_CENSUS"].sum()])
        ## Total white people (census) divided by total population (census)
        addyResults.extend([returnAddy["WHITE_POP_VEH_CENSUS"].sum() / returnAddy["TOTAL_POP_CENSUS"].sum()])
        ## Expected total black people (percent of Zip that's black (census), times total number of citations for that zip) divided by total number of citations
        addyResults.extend([(returnAddy["BLACK_PCT_CENSUS"] * returnAddy["COUNT"]).sum() / returnAddy["COUNT"].sum()])
        ## Expected total white people (percent of Zip that's black (census), times total number of citations for that zip) divided by total number of citations
        addyResults.extend([(returnAddy["WHITE_PCT_CENSUS"] * returnAddy["COUNT"]).sum() / returnAddy["COUNT"].sum()])
        # Percentage point difference from observed percent black (citations) to expected percent black (census)
        addyResults.extend([addyResults[1]-addyResults[4]])
        # Percentage point difference from observed percent white (citations) to expected percent white (census)
        addyResults.extend([(1-addyResults[1])-addyResults[5]])
        # Calculate two-sample difference of proportions test
        count = np.array([returnAddy["SUM"].sum(), returnAddy["BLACK_POP_VEH_CENSUS"].sum()])
        nobs = np.array([returnAddy["COUNT"].sum(), returnAddy["TOTAL_POP_CENSUS"].sum()])
        z1, pval = sm.stats.proportions_ztest(count, nobs)
        addyResults.extend([pval])
        resultsDF = resultsDF.append([addyResults])

    columnsList = ['YEAR','BLACK_PCT_CITATIONS','BLACK_PCT_CENSUS','WHITE_PCT_CENSUS','WEIGHT_BLACK_PCT_CENSUS','WEIGHT_WHITE_PCT_CENSUS','BLACK_PCT_DIFF','WHITE_PCT_DIFF','BLACK_PVAL']
    resultsDF.columns = columnsList
    resultsDF.to_csv(filename + "_census_Results" + filetype)

## Filtering criteria Male/Female/All, age in years, All/Young(16-24)/Old(25+)
gender = "All"
age = (0,150)
ageCategory="All"
# years=[(2011,2011),(2012,2012),(2013,2013),(2014,2014),(2015,2015),(2016,2016),(2017,2017),(2011,2017)]
years=[(2011,2017)]

## Filtering on one year
# filterResults(years)

## Bootstrap analysis
# bootstrapAnalysis()

## Veil of Darkness analysis
# veilAnalysis(years)

## Census benchmark
censusBenchmark(years)