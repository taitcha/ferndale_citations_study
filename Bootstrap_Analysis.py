
from scipy import stats
import numpy as np
import Address_Analysis as addy
import bootstrapped.bootstrap as bs
import bootstrapped.stats_functions as bs_stats

filetype = ".csv"

def runBootstrap(citations):
    ### Citations Distribution ###
    # Convert citations race to binomial
    citations["Offender Race"] = citations.apply(lambda row: 0 if row["Offender Race"] == "W" else 1, axis=1)

    samplesCitationList = []
    numIterations = 5000
    numSamples = 70000
    numBins = 100

    ## Get bootstrap sample for citations
    for n in (range(numIterations)):
        sampleCitations = citations["Offender Race"].sample(n=numSamples, replace=True).values
        samplesCitationList.append(np.mean(sampleCitations))

    print("Citations mean: ", np.mean(samplesCitationList))
    print("Citations std: ", np.std(samplesCitationList))

    ## Show histogram of citations bootstrap distribution
    # count, bins, ignored = plt.hist(samplesCitationList, numBins)
    # plt.title('Distribution of % Black Citations sample')
    # plt.show()

    ### Census Distribution ###
    ## Load up Census data
    returnAddy = addy.runAddress(citations)
    returnAddy.reset_index(drop=True, inplace=True)

    ## Get bootstrap sample for census
    samplesCensusList = []

    for n in (range(numIterations)):
        samplesCensusListZip = []
        for zip in returnAddy.itertuples():
            # print(zip.COUNT)
            sampleCensus = np.random.binomial(1, zip.BLACK_PCT_CENSUS, zip.COUNT)
            samplesCensusListZip.extend(sampleCensus)
        samplesCensusList.append(np.mean(samplesCensusListZip))

    print("Census mean: ", np.mean(samplesCensusList))
    print("Census std: ", np.std(samplesCensusList))

    ## Show histogram of census bootstrap distribution
    # count, bins, ignored = plt.hist(samplesCensusList, numBins)
    # plt.title('Distribution of % Black Census sample')
    # plt.show()

    ## Compare census to citation samples using Wilcoxon signed-rank test
    z_statistic, p_value = stats.wilcoxon(samplesCitationList, samplesCensusList)

    print("Results of Wilcoxon signed-rank test: ")
    print(p_value)

    return