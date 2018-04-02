import datetime
import pandas as pd

def filterData(citations, startYear, endYear, gender="All", age=(0,150)):
    ## Track how many citations the previous filters already took out
    countFiltered = 0

    ## Exclude to certain dates (year/month/day)
    startDate = datetime.date(startYear, 1, 1)
    endDate = datetime.date(endYear, 12, 31)
    citationsF = citations[(citations['Citation Date_x'] >= startDate)
                                 & (citations['Citation Date_x'] <= endDate)]
    DATE_EXCL = (len(citations.index)-len(citationsF.index))-countFiltered
    print("Date excluded: ", DATE_EXCL)
    countFiltered += DATE_EXCL

    ## Exclude Parking violations (officer can't tell the race of the driver)
    citationsF = citationsF[~citationsF['Violation Category'].str.contains("PARKING",na=False)]
    PARK_VIOL_EXCL = (len(citations.index) - len(citationsF.index))-countFiltered
    print("Number of Parking violations excluded: ", PARK_VIOL_EXCL)
    countFiltered += PARK_VIOL_EXCL

    ## Exclude citations that don't include race of driver (blank or "U" for unknown, "A" for Asian, "I" for Indian since there's so few)
    citationsF = citationsF[(citationsF['Offender Race'] != "U")
                               & (citationsF['Offender Race'] != "A")
                               & (citationsF['Offender Race'] != "I")]
    RACE_EXCL = (len(citations.index) - len(citationsF.index))-countFiltered
    print("Number of Race (Unknown, or Asian) excluded: ", RACE_EXCL)
    countFiltered += RACE_EXCL

    raceCount = citations["Offender Race"].value_counts()
    RACE_B = raceCount["B"]
    RACE_W = raceCount["W"]
    try:
        RACE_U = raceCount["U"]
    except:
        RACE_U = 0
    try:
        RACE_A = raceCount["A"]
    except:
        RACE_A = 0
    try:
        RACE_I = raceCount["I"]
    except:
        RACE_I = 0

    print("Original Race Counts: ")
    print(raceCount)

    ## Plot raceCount
    # raceCount.plot.bar()
    # plt.show()

    ## Exclude rows that have blanks for Race, Sex, Address, City, State, Zip, DOB
    citationsF = citationsF[~citationsF['Offender Race'].isnull()
                               & (~citationsF['Offender Sex Description'].isnull())
                               & (~citationsF['Offender Address'].isnull())
                               & (~citationsF['Offender City'].isnull())
                               & (~citationsF['Offender State'].isnull())
                               & (~citationsF['Offender Zip Code'].isnull())]
    BLANK_EXCL = (len(citations.index) - len(citationsF.index))-countFiltered
    print("Rows with blanks excluded: ", BLANK_EXCL)
    countFiltered += BLANK_EXCL

    ## Exclude to Michigan only
    citationsF = citationsF[citationsF["Offender State"]=="MI"]
    MI_EXCL = (len(citations.index)-len(citationsF.index))-countFiltered
    print("Non-MI excluded: ", MI_EXCL)
    countFiltered += MI_EXCL

    ## Exclude duplicate CitationID rows, as they represent multiple citations for the same stop & person
    citationsF = citationsF.drop_duplicates(subset=["Citation Number"], keep="last")
    DUPE_EXCL = (len(citations.index) - len(citationsF.index))-countFiltered
    print("Rows with blanks excluded: ", DUPE_EXCL)
    countFiltered += DUPE_EXCL

    ## Filter by gender if desired
    if gender == "Male":
        citationsF = citationsF[citationsF["Offender Sex Description"] == "Male"]
        GEN_EXCL = (len(citations.index) - len(citationsF.index)) - countFiltered
        print("Females excluded: ", GEN_EXCL)
        countFiltered += GEN_EXCL
    elif gender == "Female":
        citationsF = citationsF[citationsF["Offender Sex Description"] == "Female"]
        GEN_EXCL = (len(citations.index) - len(citationsF.index)) - countFiltered
        print("Males excluded: ", GEN_EXCL)
        countFiltered += GEN_EXCL

    ## Filter by age if desired
    citationsF = citationsF[((citationsF['Citation Date_x'].dt.year- citationsF['BD_DATE'].dt.year) >= age[0])
                           & ((citationsF['Citation Date_x'].dt.year - citationsF['BD_DATE'].dt.year) <= age[1])]
    AGE_EXCL = (len(citations.index)-len(citationsF.index))-countFiltered
    print("Age excluded: ", AGE_EXCL)
    countFiltered += AGE_EXCL

    TOTAL_EXCL = len(citations.index)-len(citationsF.index)
    TOTAL_FILT = len(citationsF.index)
    print("Total filtered: ", TOTAL_EXCL, " out of ", len(citations.index), " records, ", TOTAL_FILT, " total remain")
    return citationsF, [PARK_VIOL_EXCL,RACE_EXCL,RACE_B,RACE_W,RACE_A,RACE_U,RACE_I,BLANK_EXCL,MI_EXCL,DATE_EXCL,TOTAL_EXCL,TOTAL_FILT]