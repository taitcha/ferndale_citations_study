import datetime
import pandas as pd

def filterData(citations, startYear, endYear):
    ## Exclude to certain dates (year/month/day)
    startDate = datetime.date(startYear, 1, 1)
    endDate = datetime.date(endYear, 12, 31)
    citationsD = citations[(citations['Citation Date_x'] >= startDate)
                                 & (citations['Citation Date_x'] <= endDate)]
    DATE_EXCL = len(citations.index)-len(citationsD.index)
    print("Date excluded: ", DATE_EXCL)

    # Exclude Parking violations (officer can't tell the race of the driver)
    citationsDP = citationsD[~citationsD['Violation Category'].str.contains("PARKING",na=False)]
    PARK_VIOL_EXCL = len(citationsD.index) - len(citationsDP.index)
    print("Number of Parking violations excluded: ", PARK_VIOL_EXCL)

    # Exclude citations that don't include race of driver (blank or "U" for unknown, "A" for Asian, "I" for Indian since there's so few)
    citationsDPR = citationsDP[(citationsDP['Offender Race'] != "U")
                               & (citationsDP['Offender Race'] != "A")
                               & (citationsDP['Offender Race'] != "I")]
    RACE_EXCL = len(citationsDP.index) - len(citationsDPR.index)
    print("Number of Race (Unknown, or Asian) excluded: ", RACE_EXCL)

    raceCount = citationsDP["Offender Race"].value_counts()
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

    ## Plot raceCount
    # raceCount.plot.bar()
    # plt.show()

    # Exclude rows that have blanks for Race, Sex, Address, City, State, Zip
    citationsDPRB = citationsDPR[~citationsDPR['Offender Race'].isnull()
                               & (~citationsDPR['Offender Sex Description'].isnull())
                               & (~citationsDPR['Offender Address'].isnull())
                               & (~citationsDPR['Offender City'].isnull())
                               & (~citationsDPR['Offender State'].isnull())
                               & (~citationsDPR['Offender Zip Code'].isnull())]
    BLANK_EXCL = len(citationsDPR.index) - len(citationsDPRB.index)
    print("Rows with blanks excluded: ", BLANK_EXCL)

    # Exclude to Michigan only
    citationsMI = citationsDPRB[citationsDPRB["Offender State"]=="MI"]
    MI_EXCL = len(citationsDPRB.index)-len(citationsMI.index)
    print("Non-MI excluded: ", MI_EXCL)

    TOTAL_EXCL = len(citations.index)-len(citationsDPRB.index)
    TOTAL_FILT = len(citationsDPRB.index)
    print("Total filtered: ", TOTAL_FILT, " out of ", len(citations.index), " records, ", TOTAL_EXCL, " total")
    return citationsDPRB, [PARK_VIOL_EXCL,RACE_EXCL,RACE_B,RACE_W,RACE_A,RACE_U,RACE_I,BLANK_EXCL,MI_EXCL,DATE_EXCL,TOTAL_EXCL,TOTAL_FILT]