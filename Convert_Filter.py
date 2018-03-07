import datetime
import pandas as pd
import Veil_Darkness as veil
import Address_Analysis as addy
# import statsmodels.api as sm
# import statsmodels.formula.api as smf
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns


def filterData(citations, yearFilter):
    # Exclude to certain dates (year/month/day)
    startDate = datetime.date(yearFilter, 1, 1)
    endDate = datetime.date(yearFilter, 12, 31)
    citationsD = citations[(citations['CITATION_DT'] >= startDate)
                                 & (citations['CITATION_DT'] <= endDate)]
    DATE_EXCL = len(citations.index)-len(citationsD.index)
    print("Date excluded: ", DATE_EXCL)

    # Exclude Parking violations (officer can't tell the race of the driver)
    citationsDP = citationsD[~citationsD['VIOLS_DESC'].str.contains("Parking -",na=False)]
    PARK_VIOL_EXCL = len(citationsD.index) - len(citationsDP.index)
    print("Number of Parking violations excluded: ", PARK_VIOL_EXCL)

    # Exclude citations that don't include race of driver (blank or "U" for unknown, "A" for Asian since there's so few)
    citationsDPR = citationsDP[(citationsDP['OFF_RACE_CD'] != "U")
                             & (citationsDP['OFF_RACE_CD'] != "A")]
    RACE_EXCL = len(citationsDP.index) - len(citationsDPR.index)
    print("Number of Race (Unknown, or Asian) excluded: ", RACE_EXCL)

    raceCount = citationsDP["OFF_RACE_CD"].value_counts()
    RACE_B = raceCount["B"]
    RACE_W = raceCount["W"]
    RACE_U = raceCount["U"]
    if "A" in raceCount:
        RACE_A = raceCount["A"]
    else:
        RACE_A = 0
    if "I" in raceCount:
        RACE_I = raceCount["I"]
    else:
        RACE_I = 0
    print("Original Race Counts: ")
    print(raceCount)

    #Plot raceCount
    # raceCount.plot.bar()
    # plt.show()

    # Exclude rows that have blanks for Race, Sex, Address, City, State, Zip
    citationsDPRB = citationsDPR[~citationsDPR['OFF_RACE_CD'].isnull()
                               & (~citationsDPR['OFF_SEX_CD'].isnull())
                               & (~citationsDPR['OFF_ADDRESS_TXT'].isnull())
                               & (~citationsDPR['OFF_CITY_NM'].isnull())
                               & (~citationsDPR['OFF_STATE_CD'].isnull())
                               & (~citationsDPR['OFF_ZIP_CD'].isnull())]
    BLANK_EXCL = len(citationsDPR.index) - len(citationsDPRB.index)
    print("Rows with blanks excluded: ", BLANK_EXCL)

    # Exclude to Michigan only
    citationsMI = citationsDPRB[citationsDPRB["OFF_STATE_CD"]=="MI"]
    MI_EXCL = len(citationsDPRB.index)-len(citationsMI.index)
    print("Non-MI excluded: ", MI_EXCL)

    TOTAL_EXCL = len(citations.index)-len(citationsDPRB.index)
    TOTAL_FILT = len(citationsDPRB.index)
    print("Total filtered: ", TOTAL_FILT, " out of ", len(citations.index), " records, ", TOTAL_EXCL, " total")
    return citationsDPRB, [PARK_VIOL_EXCL,RACE_EXCL,RACE_B,RACE_W,RACE_A,RACE_U,RACE_I,BLANK_EXCL,MI_EXCL,DATE_EXCL,TOTAL_EXCL,TOTAL_FILT]

##### Import and filtering #####

# Read in original CSV citations
filename = "FerndaleCitations2009_2017"
# filename = "FerndaleCitationsSample"
filetype = ".csv"

parseDates = ['CITATION_DT','FORM_CITATION_DT']


# Read pickle instead of csv to speed up processing
# rawData = pd.read_csv(filename + filetype, parse_dates=parseDates, header=0, low_memory=False)
# rawData.to_pickle(filename + ".pkl")
rawData = pd.read_pickle(filename + ".pkl")

citations = pd.DataFrame(rawData)

## Do filtering if not already done
citations, citationsResults = filterData(citations, 2012)
citations.to_csv(filename + "_filtered" + filetype)

## Run Veil of Darkness analysis
# returnVeil = veil.runVeil(citations, filename)

## Run Address analysis
# returnAddy = addy.runAddress(citations, filename)
# print("Weighted average Black percent for citations: ")
# print((returnAddy["BLACK_PCT_CITATIONS"] * returnAddy["COUNT"]).sum() / returnAddy["COUNT"].sum())
# print("Weighted average Black percent for census: ")
# print((returnAddy["BLACK_PCT_CENSUS"] * returnAddy["HC01_VC03"]).sum() / returnAddy["HC01_VC03"].sum())
# print("Weighted average Black percent for census weighted by citations: ")
# print((returnAddy["BLACK_PCT_CENSUS"] * returnAddy["COUNT"]).sum() / returnAddy["COUNT"].sum())
# returnAddy.to_csv("addyresult.csv")

## Write results to file
# columnsList = ['PARK_VIOL_EXCL', 'RACE_EXCL','RACE_B','RACE_W','RACE_A','RACE_U','RACE_I','BLANK_EXCL','MI_EXCL','DATE_EXCL','TOTAL_EXCL','TOTAL_FILT','EARLY_SUNSET','LATE_SUNSET','ODDS_RATIO','DAY_VEIL_P','DAY_VEIL_STDERROR','BLACK_CNT_DAY','BLACK_CNT_NIGHT','TOTAL_DAY','TOTAL_NIGHT','BLACK_PCT_DAY','BLACK_PCT_NIGHT','TWO_SAMPLE_DIFF']
#
# citationsResults.extend(returnVeil)
# resultsDF = pd.DataFrame()
# resultsDF = resultsDF.append([citationsResults])
# resultsDF.columns = columnsList
# resultsDF.to_csv(filename + "_Results" + filetype)

## Loop through multiple years
# years=[2009,2010,2011,2012,2013,2014,2015,2016,2017]
# resultsDF = pd.DataFrame()
#
# for year in years:
#     citations = pd.DataFrame(rawData)
#     citations, citationsResults = filterData(citations, year)
#     returnVeil = veil.runVeil(citations, filename)
#     citationsResults.extend(returnVeil)
#     citationsResults.extend([year])
#     resultsDF = resultsDF.append([citationsResults])
#
# columnsList = ['PARK_VIOL_EXCL', 'RACE_EXCL','RACE_B','RACE_W','RACE_A','RACE_U','RACE_I','BLANK_EXCL','MI_EXCL','DATE_EXCL','TOTAL_EXCL','TOTAL_FILT','EARLY_SUNSET','LATE_SUNSET','ODDS_RATIO','DAY_VEIL_P','DAY_VEIL_STDERROR','BLACK_CNT_DAY','BLACK_CNT_NIGHT','TOTAL_DAY','TOTAL_NIGHT','BLACK_PCT_DAY','BLACK_PCT_NIGHT','TWO_SAMPLE_DIFF',"YEAR"]
# resultsDF.columns = columnsList
# resultsDF.to_csv(filename + "_Results" + filetype)


# Get percent black for each year
years=[2009,2010,2011,2012,2013,2014,2015,2016,2017]
resultsDF = pd.DataFrame()
racePctYear = []


for year in years:
    citations = pd.DataFrame(rawData)
    citations, citationsResults = filterData(citations, year)

    raceCount = citations["OFF_RACE_CD"].value_counts()
    returnAddy = addy.runAddress(citations, filename)
    addyResults = []
    addyResults.extend([year])
    addyResults.extend([raceCount["B"]/citations.shape[0]])
    addyResults.extend([(returnAddy["BLACK_PCT_CITATIONS"] * returnAddy["COUNT"]).sum() / returnAddy["COUNT"].sum()])
    addyResults.extend([(returnAddy["BLACK_PCT_CENSUS"] * returnAddy["HC01_VC03"]).sum() / returnAddy["HC01_VC03"].sum()])
    addyResults.extend([(returnAddy["BLACK_PCT_CENSUS"] * returnAddy["COUNT"]).sum() / returnAddy["COUNT"].sum()])
    addyResults.extend([addyResults[2]-addyResults[4]])
    resultsDF = resultsDF.append([addyResults])

columnsList = ['YEAR','BLACK_PCT','WEIGHT_BLACK_PCT_CITATIONS','WEIGHT_BLACK_PCT_CENSUS','WEIGHT_BLACK_PCT_CENSUS_BY_CITATION','PCT_DIFF']
resultsDF.columns = columnsList
resultsDF.to_csv("addy_Results" + filetype)


print(racePctYear)
