
import datetime
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import numpy as np
import matplotlib.pyplot as plt

filetype = ".csv"

def isolateZip(citation):
    if citation[:5].isdigit():
        return int(citation[:5])
    else:
        return

def diffProp(firstIn,firstTot,secondIn,secondTot):
    count = np.array([firstIn, secondIn])
    nobs = np.array([firstTot, secondTot])
    z1, pval = sm.stats.proportions_ztest(count, nobs)
    # print("Two-sample difference of proportions: ", '{0:0.7f}'.format(pval))
    return round(pval,5)

def runAddress(citations):
    citationsA = citations.copy()
    # Convert W to 0, B to 1 to make processing race stats easier
    citationsA["Offender Race"] = citationsA.apply(lambda row: 0 if row["Offender Race"] == "W" else 1, axis=1)

    # Isolate 5-digit ZIP
    citationsA["ZIP5"] = citationsA["Offender Zip Code"].apply(isolateZip)

    # Calculate percent black
    groupZip = citationsA.groupby("ZIP5")["Offender Race"].agg({'SUM': 'sum', "MEAN": 'mean', "COUNT": 'count'})


    # Join with census data by zip
    filenameCensus = "ACS_16_5YR_DP05_with_ann"
    filetype = ".csv"

    censusData = pd.read_csv(filenameCensus + filetype, header=0,skiprows=[1])
    censusData.rename(columns={'GEO.id2': 'ZIP5'}, inplace=True)
    censusData = censusData.set_index('ZIP5')

    zipJoin = groupZip.merge(censusData, left_index=True, right_index=True)

    zipJoin = zipJoin.filter(["SUM",
                              "MEAN",
                              "COUNT",
                              "HC01_VC03","HC02_VC03",
                              "HC01_VC50","HC02_VC50",
                              "HC03_VC50","HC04_VC50",
                              "HC01_VC79","HC02_VC79",
                              "HC03_VC79","HC04_VC79"])

    # Filter out low-count zip codes
    zipJoin = zipJoin.query('COUNT>10')

    #Calculate two-sample difference of proportions
    zipJoin["DIFF_PROP_P"] = zipJoin.apply(lambda row: diffProp(row["SUM"],row["COUNT"],row["HC01_VC79"],row["HC01_VC03"]), axis=1)

    # Throw in the % black for each zip, by citations and census
    zipJoin["BLACK_PCT_CITATIONS"] = zipJoin.apply(lambda row: row["SUM"]/row["COUNT"], axis=1)
    zipJoin["BLACK_PCT_CENSUS"] = zipJoin.apply(lambda row: row["HC01_VC79"]/row["HC01_VC03"], axis=1)

    return zipJoin