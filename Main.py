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

# ### Do filtering on one year and export to csv
# startYear = 2016
# endYear = 2016
# citations, citationsResults = filt.filterData(citations, startYear, endYear, gender="All", age=(0,99))
# citations.to_csv(filename + "_filtered" + filetype)

## Run Bootstrap analysis
# citations, citationsResults = filt.filterData(citations, 2011, 2017)
# bootstrapResults = boot.runBootstrap(citations)

## Write Veil of Darkness results to file for each year & all years
years=[(2011,2011),(2012,2012),(2013,2013),(2014,2014),(2015,2015),(2016,2016),(2017,2017),(2011,2017)]
resultsDF = pd.DataFrame()

for year in years:
    citations = pd.DataFrame(rawData)
    citations, citationsResults = filt.filterData(citations, year[0], year[1], gender="All", age=(0,150))
    returnVeil = veil.runVeil(citations, filename)
    citationsResults.extend(returnVeil)
    citationsResults.extend([year])
    resultsDF = resultsDF.append([citationsResults])

columnsList = ['PARK_VIOL_EXCL', 'RACE_EXCL','RACE_B','RACE_W','RACE_A','RACE_U','RACE_I','BLANK_EXCL','MI_EXCL','DATE_EXCL','TOTAL_EXCL','TOTAL_FILT','EARLY_SUNSET','LATE_SUNSET','ODDS_RATIO','DAY_VEIL_P','DAY_VEIL_STDERROR','BLACK_CNT_DAY','BLACK_CNT_NIGHT','TOTAL_DAY','TOTAL_NIGHT','BLACK_PCT_DAY','BLACK_PCT_NIGHT','TWO_SAMPLE_DIFF',"YEAR"]
resultsDF.columns = columnsList
resultsDF.to_csv(filename + "_VoD_Results" + filetype)

## Get Address Analysis percent black for each year & all years
years=[(2011,2011),(2012,2012),(2013,2013),(2014,2014),(2015,2015),(2016,2016),(2017,2017),(2011,2017)]
resultsDF = pd.DataFrame()
racePctYear = []

for year in years:
    citations = pd.DataFrame(rawData)
    citations, citationsResults = filt.filterData(citations, year[0], year[1], gender="All", age=(0,150))

    raceCount = citations["Offender Race"].value_counts()
    returnAddy = addy.runAddress(citations)
    addyResults = []
    addyResults.extend([year])
    ## Total black drivers divided by total citations
    addyResults.extend([returnAddy["SUM"].sum() / returnAddy["COUNT"].sum()])
    ## Total black people (census) divided by total population (census)
    addyResults.extend([returnAddy["BLACK_POP_VEH_CENSUS"].sum() / returnAddy["HC01_EST_VC01"].sum()])
    ## Expected total black people (percent of Zip that's black (census), times total number of citations for that zip) divided by total number of citations
    addyResults.extend([(returnAddy["BLACK_PCT_CENSUS"] * returnAddy["COUNT"]).sum() / returnAddy["COUNT"].sum()])
    # Percentage point difference from observed percent black (citations) to expected percent black (census)
    addyResults.extend([addyResults[1]-addyResults[3]])
    # Calculate two-sample difference of proportions test
    count = np.array([returnAddy["SUM"].sum(), returnAddy["BLACK_POP_VEH_CENSUS"].sum()])
    nobs = np.array([returnAddy["COUNT"].sum(), returnAddy["HC01_EST_VC01"].sum()])
    z1, pval = sm.stats.proportions_ztest(count, nobs)
    addyResults.extend([pval])
    resultsDF = resultsDF.append([addyResults])

columnsList = ['YEAR','BLACK_PCT_CITATIONS','WEIGHT_BLACK_PCT_CENSUS','WEIGHT_BLACK_PCT_CENSUS_BY_CITATION','PCT_DIFF','PVAL']
resultsDF.columns = columnsList
resultsDF.to_csv("addy_Results" + filetype)