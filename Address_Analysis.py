
import datetime
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import numpy as np
import matplotlib.pyplot as plt

filename = "CitationsQuery2_complete"
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
    return round(pval,6)

def runAddress(citations, gender="All", age="All"):
    citationsA = citations.copy()
    ## Convert W to 0, B to 1 to make processing race stats easier
    citationsA["Offender Race"] = citationsA.apply(lambda row: 0 if row["Offender Race"] == "W" else 1, axis=1)

    ## Isolate 5-digit ZIP
    citationsA["ZIP5"] = citationsA["Offender Zip Code"].apply(isolateZip)

    ## Calculate percent black
    groupZip = citationsA.groupby("ZIP5")["Offender Race"].agg({'SUM': 'sum', "MEAN": 'mean', "COUNT": 'count'})

    ## Join with census data by zip
    filenameCensus = "ACS_16_5YR_S0802_with_ann"
    filetype = ".csv"

    censusData = pd.read_csv(filenameCensus + filetype, header=0,skiprows=[1])
    censusData.rename(columns={'GEO.id2': 'ZIP5'}, inplace=True)
    censusData = censusData.set_index('ZIP5')

    ## Get rid of non-numeric values
    censusData.replace("-",0,inplace=True)
    censusData.replace("**", 0, inplace=True)
    censusData.replace("(X)", 0, inplace=True)

    zipJoin = groupZip.merge(censusData, left_index=True, right_index=True)

    zipJoin = zipJoin.filter(["SUM",
                              "MEAN",
                              "COUNT",
                              "HC01_EST_VC01","HC01_EST_VC19",
                              "HC01_EST_VC18","HC01_EST_VC126",
                              "HC01_EST_VC13","HC01_EST_VC14",
                              "HC01_EST_VC03","HC01_EST_VC04"])

    ## Filter out low-citation-count zip codes if desired
    # zipJoin = zipJoin.query('COUNT>30')

    ## Make sure it's all floats rather than strings
    zipJoin = zipJoin.astype(float)
    zipFieldlist = ["BLACK_POP_CENSUS","WHITE_POP_CENSUS","TOTAL_POP_CENSUS"]

    ## Calculate total black & white populations per ZIP (one race)
    zipJoin["BLACK_POP_CENSUS"] = zipJoin.apply(lambda row: row["HC01_EST_VC01"] * (row["HC01_EST_VC19"]/100), axis=1)
    zipJoin["WHITE_POP_CENSUS"] = zipJoin.apply(lambda row: row["HC01_EST_VC01"] * (row["HC01_EST_VC18"]/100), axis=1)
    zipJoin["TOTAL_POP_CENSUS"] = zipJoin.apply(lambda row: row["HC01_EST_VC01"], axis=1)

    ## Adjust census numbers if gender filter is on
    if gender == "Male":
        for field in zipFieldlist:
            zipJoin[field] = zzipJoin.apply(lambda row: row[field] * (row["HC01_EST_VC13"]/100), axis=1)
    elif gender == "Female":
        for field in zipFieldlist:
            zipJoin[field] = zzipJoin.apply(lambda row: row[field] * (row["HC01_EST_VC14"]/100), axis=1)

    ## Adjust census numbers if age filter is on (young== 16-24, old==25+)
    if age == "Young":
        for field in zipFieldlist:
            zipJoin[field] = zipJoin.apply(lambda row: row[field] * ((row["HC01_EST_VC03"]+row["HC01_EST_VC04"])/100), axis=1)
    elif age == "Old":
        for field in zipFieldlist:
            zipJoin[field] = zipJoin.apply(lambda row: row[field] * (1-((row["HC01_EST_VC03"]+row["HC01_EST_VC04"])/100)), axis=1)

    ## Calculate total black & white with access to vehicle
    zipJoin["BLACK_POP_VEH_CENSUS"] = zipJoin.apply(lambda row: row["BLACK_POP_CENSUS"]*(1-(row["HC01_EST_VC126"]/100)), axis=1)
    zipJoin["WHITE_POP_VEH_CENSUS"] = zipJoin.apply(lambda row: row["WHITE_POP_CENSUS"]*(1-(row["HC01_EST_VC126"]/100)), axis=1)

    ## Calculate two-sample difference of proportions
    zipJoin["DIFF_PROP_P"] = zipJoin.apply(lambda row: diffProp(row["SUM"],row["COUNT"],row["BLACK_POP_VEH_CENSUS"],row["TOTAL_POP_CENSUS"]), axis=1)

    ## Throw in the % black for each zip, by citations and census
    zipJoin["BLACK_PCT_CITATIONS"] = zipJoin.apply(lambda row: row["SUM"]/row["COUNT"], axis=1)
    zipJoin["BLACK_PCT_CENSUS"] = zipJoin.apply(lambda row: row["BLACK_POP_VEH_CENSUS"]/row["TOTAL_POP_CENSUS"], axis=1)
    zipJoin["WHITE_PCT_CENSUS"] = zipJoin.apply(lambda row: row["WHITE_POP_VEH_CENSUS"]/row["TOTAL_POP_CENSUS"], axis=1)

    zipJoin.to_csv(filename + "_zipJoin" + filetype)

    return zipJoin

    ##### RAW POPULATION CENSUS DATA CODE #####
    # ## Join with census data by zip
    # filenameCensus = "ACS_16_5YR_DP05_with_ann"
    # filetype = ".csv"
    #
    # censusData = pd.read_csv(filenameCensus + filetype, header=0,skiprows=[1])
    # censusData.rename(columns={'GEO.id2': 'ZIP5'}, inplace=True)
    # censusData = censusData.set_index('ZIP5')
    #
    # zipJoin = groupZip.merge(censusData, left_index=True, right_index=True)
    #
    # zipJoin = zipJoin.filter(["SUM",
    #                           "MEAN",
    #                           "COUNT",
    #                           "HC01_VC03","HC02_VC03",
    #                           "HC01_VC50","HC02_VC50",
    #                           "HC03_VC50","HC04_VC50",
    #                           "HC01_VC79","HC02_VC79",
    #                           "HC03_VC79","HC04_VC79"])
    #
    # ## Calculate two-sample difference of proportions
    # zipJoin["DIFF_PROP_P"] = zipJoin.apply(lambda row: diffProp(row["SUM"],row["COUNT"],row["HC01_VC79"],row["HC01_VC03"]), axis=1)
    #
    # zipJoin["BLACK_PCT_CENSUS"] = zipJoin.apply(lambda row: row["HC01_VC79"] / row["HC01_VC03"], axis=1)
    ##### END RAW POPULATION CENSUS DATA CODE #####