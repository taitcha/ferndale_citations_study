import datetime
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import numpy as np
import matplotlib.pyplot as plt
from astral import Astral
import pytz
# import seaborn as sns

pd.options.mode.chained_assignment = None  # default='warn'

filetype = ".csv"


def percent_sample_awesome_plot(big_df, x, y, hue, col=None, smoothing=1, n_samples=10000, xlabel='', ylabel='',
                                relabeling=None, colors=None):
    hues = set(big_df[hue])

    grouped = big_df.groupby(x)
    df_for_plot = []
    for x_val, group in grouped:
        raw_counts = []
        # print x_val, group[[hue, y]]
        for row in group[[hue, y]].itertuples():
            hue_name = row[1]
            # Generate a long list of how many times this particular hue occurred
            for i in range(row[2]):
                raw_counts.append(hue_name)

        # Sample from the total counts to bootstrap the percentages of how many times each hue occurs
        n = len(raw_counts)
        nf = float(n)
        hue_to_probs = defaultdict(list)
        for i in range(n_samples):
            sample = np.random.choice(raw_counts, n)
            counts = Counter(sample)
            for h in hues:
                hue_to_probs[h].append(counts[h] / nf)

        # print hue_to_probs
        for h, probs in hue_to_probs.iteritems():
            bleh = {}
            df_for_plot.append(bleh)

            probs.sort()
            bleh['X'] = x_val
            bleh['Hue'] = h
            bleh['Mean'] = probs[len(probs) / 2]
            bleh['Upper Bound'] = probs[(19 * len(probs)) / 20]  # 95%
            bleh['Lower Bound'] = probs[len(probs) / 20]  # 5%
    df_for_plot = pd.DataFrame(df_for_plot)

    mycolors = [

        '#66a61e',

        '#e7298a',
        '#7570b3',
        '#1b9e77',

        '#e6ab02',
        '#d95f02',

    ]

    if colors is None:
        colors = mycolors

    styles = ['-', '--', '-.', ':', '-']
    for j, h in enumerate(hues):
        sub_df = df_for_plot[df_for_plot['Hue'] == h]
        xs = sub_df['X']

        attr_mean = sub_df['Mean']

        # print h, attr_mean

        lower_bound = sub_df['Lower Bound']
        upper_bound = sub_df['Upper Bound']

        label = h
        if relabeling is not None:
            if label in relabeling:
                label = relabeling[label]

        plt.plot(xs, attr_mean, \
                 label=label, color=colors[j % len(colors)], ls=styles[j % len(styles)])

        plt.fill_between(xs, lower_bound, upper_bound, \
                         interpolate=False, alpha=0.1, edgecolor=None, \
                         color=colors[j % len(colors)])

    plt.legend(ncol=1, fontsize=24, loc='upper left', bbox_to_anchor=(1., 0.8))
    plt.gca().set_axis_bgcolor('white')

    ax = plt.gca()
    ax.set_ylabel(ylabel, fontsize=22)
    ax.set_xlabel(xlabel, fontsize=22)
    ax.grid(False)
    plt.tight_layout()

##### Veil of Darkness analysis #####

def addTimeZone(naiveDate):
    local = pytz.timezone("America/Detroit")
    newDate = local.localize(naiveDate)
    return newDate

def runVeil(citations, filename, year):
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
    date = datetime.date(year[0], 1, 1)
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

    # sampleDayNight = pd.concat([sampleDay,sampleNight],axis=1,join_axes=[sampleDay.index])
    # sampleDayNight.columns = sampleDayNight.columns.get_level_values(0)
    sampleDayNight = sampleDay.merge(sampleNight, left_index=True, right_index=True)
    sampleDayNight = sampleDayNight.filter(["SAMEDATE","DAYLIGHT","DARKNESS"])

    print(sampleDayNight.head())
#    percent_sample_awesome_plot(sampleDayNight, x="TIME", y="SAMEDATE")

    colors = [(86/255,  129/255,  194/255),(222/255,  113/255,  38/255)]
    sampleDayNight.plot(figsize=(8,5),color=colors)
    plt.xlabel('Percent stops of black drivers over time ' + str(year[0]) + "-"+ str(year[1]))
    # plt.show()
    plt.savefig("VoDFigure_" + str(year[0]) + "_"+ str(year[1]) + ".png")
    # fig = plt.figure()
    # fig.savefig("VoDFigure_" + str(year[0]) + "_"+ str(year[1]) + ".png")
    # plt.close()

    # # Plot regression line
    # sns.regplot(x='Citation Date_x', y="Offender Race", data=citations)
    # plt.show()
    # plt.close()

    return [earlySunset, lateSunset, ODDS_RATIO,DAY_VEIL_P,DAY_VEIL_STDERROR,blackCountDay,blackCountNight,totalDay,totalNight,BLACK_PCT_DAY,BLACK_PCT_NIGHT,TWO_SAMPLE_DIFF]