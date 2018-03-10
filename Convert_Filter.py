import datetime
import pandas as pd

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