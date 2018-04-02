import datetime
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import numpy as np
import matplotlib.pyplot as plt
from astral import Astral
import pytz

pd.options.mode.chained_assignment = None  # default='warn'

filetype = ".csv"

##### Veil of Darkness analysis #####

def addTimeZone(naiveDate):
    local = pytz.timezone("America/Detroit")
    newDate = local.localize(naiveDate)
    return newDate

def runVeil(citations, filename):
    citationsV = citations.copy()

    ## Add timezone to datetime
    citationsV["Citation Date_x"] = citationsV["Citation Date_x"].apply(addTimeZone)

    ## Make Race binary (0 = W, 1 = B)
    citationsV["Offender Race"] = citationsV.apply(lambda row: 0 if row["Offender Race"] == "W" else 1, axis=1)

    ## Add columns for Veil of Darkness analysis

    a = Astral()
    a.solar_depression = 'civil'
    city = a["Detroit"]
    timezone = city.timezone

    ## Axis = 1 for rows, 0 for columns
    citationsV["DAWN"] = citationsV.apply(lambda row: city.sun(row['Citation Date_x'])['dawn'], axis=1)
    citationsV["SUNRISE"] = citationsV.apply(lambda row: city.sun(row['Citation Date_x'])['sunrise'], axis=1)
    citationsV["DUSK"] = citationsV.apply(lambda row: city.sun(row['Citation Date_x'])['dusk'], axis=1)
    citationsV["SUNSET"] = citationsV.apply(lambda row: city.sun(row['Citation Date_x'])['sunset'], axis=1)
    citationsV["WEEKDAY"] = citationsV.apply(lambda row: row['Citation Date_x'].weekday(), axis=1)
    citationsV["TIME"] = citationsV.apply(lambda row: row['Citation Date_x'].time(), axis=1)

    ## Mark if citation is during daytime
    def checkDaylight(row):
        if (row["Citation Date_x"].time() > row["SUNRISE"].time()) and (row["Citation Date_x"].time() < row["SUNSET"].time()):
            return True
        else:
            return False

    citationsV["DAY_STRICT_FLAG"] = citationsV.apply(checkDaylight, axis=1)

    ## Compute range of dawn/dusk for the given range of values
    earlySunrise = citationsV['SUNRISE'][0].time()
    lateSunrise = citationsV['SUNRISE'][0].time()
    earlySunset = citationsV['SUNSET'][0].time()
    lateSunset = citationsV['SUNSET'][0].time()

    for index, row in citationsV.iterrows():
        if row["SUNRISE"].time() < earlySunrise:
            earlySunrise = row["SUNRISE"].time()
        if row["SUNRISE"].time() > lateSunrise:
            lateSunrise = row["SUNRISE"].time()
        if row["SUNSET"].time() < earlySunset:
            earlySunset = row["SUNSET"].time()
        if row["SUNSET"].time() > lateSunset:
            lateSunset = row["SUNSET"].time()

    def checkIntertwilight(row):
        if (row["Citation Date_x"].time() >= earlySunset) and (row["Citation Date_x"].time() <= lateSunset):
            return "Intertwilight"
        elif row["DAY_STRICT_FLAG"]:
            return "Day"
        else:
            return "Night"

    citationsV["INTERTWILIGHT_FLAG"] = citationsV.apply(checkIntertwilight, axis=1)

    print("Intertwilight periods: ")
    print("Morning: ", earlySunrise, " to ", lateSunrise)
    print("Evening: ", earlySunset, " to ", lateSunset)

    citationsV.to_csv(filename + "_VofD" + filetype)

    ## Filter to only the intertwilight period
    citationsInt = citationsV.query("INTERTWILIGHT_FLAG == 'Intertwilight'")

    ## Fit GLM regression
    formula = "citationsInt['Offender Race'] ~ WEEKDAY + DAY_STRICT_FLAG"
    result = smf.glm(formula=formula, family=sm.families.Binomial(), data=citationsInt).fit()

    print(result.params)
    print(result.summary())

    ## Calculate odds ratio between citation during day vs night
    ODDS_RATIO = np.exp(result.params["DAY_STRICT_FLAG[T.True]"])
    DAY_VEIL_P = result.pvalues["DAY_STRICT_FLAG[T.True]"]
    DAY_VEIL_STDERROR = result.bse["DAY_STRICT_FLAG[T.True]"]
    print("Odds Ratio (Day vs. Night): ", ODDS_RATIO)

    ## Calculate 95% confidence interval
    DAY_VEIL_CONF_INT = result.conf_int()
    print("Confidence interval: ", DAY_VEIL_CONF_INT)
    print("Confidence interval: ", np.exp(DAY_VEIL_CONF_INT[0][1]), np.exp(DAY_VEIL_CONF_INT[1][1]))

    ## print("Confidence interval: ", result.params["DAY_STRICT_FLAG[T.True]"].low())

    ## Calculate percent black
    blackCountDay = 0
    blackCountNight = 0
    totalDay = 0
    totalNight = 0

    for index, row in citationsInt.iterrows():
        if row["DAY_STRICT_FLAG"]:
            totalDay += 1
            if row["Offender Race"] == 1:
                blackCountDay += 1
        else:
            totalNight += 1
            if row["Offender Race"] == 1:
                blackCountNight += 1

    BLACK_PCT_DAY = blackCountDay/totalDay
    BLACK_PCT_NIGHT = blackCountNight/totalNight
    print("Black Count Day: ", blackCountDay, "/", totalDay, round(blackCountDay/totalDay,2), "%")
    print("Black Count Night: ", blackCountNight, "/", totalNight, round(blackCountNight/totalNight,2), "%")

    ## Calculate two-sample difference of proportions test
    count = np.array([blackCountDay, blackCountNight])
    nobs = np.array([totalDay, totalNight])
    z1, pval = sm.stats.proportions_ztest(count, nobs)
    TWO_SAMPLE_DIFF = pval
    print("Two-sample difference of proportions: ", '{0:0.7f}'.format(pval))

    ## Visualize in 15-minute increments
    date = datetime.date(2011, 1, 1)
    citationsInt["SAMEDATE"] = citationsInt.apply(lambda row: datetime.datetime.combine(date,row['Citation Date_x'].time()), axis=1)
    timeindexDay = citationsInt[citationsInt["DAY_STRICT_FLAG"]==True]
    timeindexDay = timeindexDay.filter(["SAMEDATE","Offender Race","DAY_STRICT_FLAG"])
    timeindexDay.columns = ["SAMEDATE","DAYLIGHT","DAY_STRICT_FLAG"]
    timeindexDay = timeindexDay.set_index('SAMEDATE')

    timeindexNight = citationsInt[citationsInt["DAY_STRICT_FLAG"]==False]
    timeindexNight = timeindexNight.filter(["SAMEDATE","Offender Race","DAY_STRICT_FLAG"])
    timeindexNight.columns = ["SAMEDATE","DARKNESS","DAY_STRICT_FLAG"]
    timeindexNight = timeindexNight.set_index('SAMEDATE')

    sampleDay = timeindexDay.resample(rule='15Min').mean()
    sampleNight = timeindexNight.resample(rule='15Min').mean()
    # print(sampleDay)
    # print(sampleNight)

    sampleDayNight = pd.concat([sampleDay,sampleNight],axis=1,join_axes=[sampleDay.index])

    sampleDayNight.plot(figsize=(8,5))
    plt.xlabel('Percent stops of black drivers, daylight and darkness')
    # plt.show()



    ## Plot regression line
    # sns.regplot(citations['Citation Date_x'],citations["Offender Race"])
    # plt.show()

    return [earlySunset, lateSunset, ODDS_RATIO,DAY_VEIL_P,DAY_VEIL_STDERROR,blackCountDay,blackCountNight,totalDay,totalNight,BLACK_PCT_DAY,BLACK_PCT_NIGHT,TWO_SAMPLE_DIFF]