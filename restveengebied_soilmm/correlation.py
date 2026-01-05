import numpy as np
from scipy import signal
import matplotlib.pyplot as plt


def ccf_values(series1, series2):
    p = series1
    q = series2
    p = (p - np.mean(p)) / (np.std(p) * len(p))
    q = (q - np.mean(q)) / (np.std(q))

    # print(p)

    c = np.correlate(p, q, "full")
    return p, q, c


def ccf_plot(lags, ccf):
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(lags, ccf)
    ax.axhline(-2 / np.sqrt(23), color="red", label=r"5% confidence interval")
    ax.axhline(2 / np.sqrt(23), color="red")
    ax.axvline(x=0, color="black", lw=1)
    ax.axhline(y=0, color="black", lw=1)
    ax.axhline(
        y=np.max(ccf),
        color="blue",
        lw=1,
        linestyle="--",
        label="highest +/- correlation",
    )
    ax.axhline(y=np.min(ccf), color="blue", lw=1, linestyle="--")
    ax.set(ylim=[-1, 1])
    ax.set_title("Cross Correlation", weight="bold", fontsize=15)
    ax.set_ylabel("Correlation Coefficients", weight="bold", fontsize=12)
    ax.set_xlabel("Time Lags", weight="bold", fontsize=12)
    plt.legend()


def crosscorr(datax, datay, lag=0):
    """Lag-N cross correlation.
    Parameters
    ----------
    lag : int, default 0
    datax, datay : pandas.Series objects of equal length

    Returns
    ----------
    crosscorr : float
    """
    return datax.corr(datay.shift(lag))


if __name__ == "__main__":
    import numpy as np
    from read import read_groundwater, read_extensometer, read_precipitation_deficit
    from layer_analysis import calculate_layer_thickness, detrend_layers

    location = "ZEG"
    groundwater = read_groundwater(location)
    extensometer = read_extensometer(location)
    precip_deficit = read_precipitation_deficit(location)

    layer_thickness = calculate_layer_thickness(extensometer)
    layer_thickness_detrended = detrend_layers(layer_thickness, detrend_method="linear")

    # what to do with Nan's?
    # groundwater = groundwater.dropna()
    # extensometer = extensometer.dropna()

    # groundwater = groundwater.loc[groundwater.index.intersection(extensometer.index)]
    # extensometer = extensometer.loc[extensometer.index.intersection(groundwater.index)]

    # groundwater = groundwater[~groundwater.index.duplicated(keep="first")]
    # extensometer = extensometer[~extensometer.index.duplicated(keep="first")]

    precip_deficit = precip_deficit.loc[
        precip_deficit.index.intersection(layer_thickness_detrended.index)
    ]
    layer_thickness_detrended = layer_thickness_detrended.loc[
        layer_thickness_detrended.index.intersection(precip_deficit.index)
    ]

    precip_deficit = precip_deficit[~precip_deficit.index.duplicated(keep="first")]
    layer_thickness_detrended = layer_thickness_detrended[
        ~layer_thickness_detrended.index.duplicated(keep="first")
    ]

    # testp, testq, testc = ccf_values(groundwater, layer_thickness_detrended["0.05 m-mv"])

    # lags = signal.correlation_lags(len(groundwater), len(layer_thickness_detrended["0.05 m-mv"]))

    # ccf_plot(lags, testc)

    lags = np.arange(
        -len(layer_thickness_detrended.index) // 2 + 1,
        len(layer_thickness_detrended.index) // 2,
    )
    lags = np.arange(-100 * 24 + 1, 100 * 24)
    # lags = np.arange(-10, 10)

    cross_corrs = []
    auto_corrs = []

    for i in lags:
        # print(i)
        cross_corrs_year = []

        for year in ["2021", "2022", "2023", "2024"]:
            precip_deficit_year = precip_deficit.loc[year]
            layer_thickness_detrended_year = layer_thickness_detrended.loc[year]

            cross_corr_year = crosscorr(
                precip_deficit_year,
                layer_thickness_detrended_year["0.41 m bs - 0.06 m bs"],
                lag=i,
            )

            cross_corrs_year.append(cross_corr_year)

        cross_corrs.append(np.mean(cross_corrs_year))
        # auto_corr = groundwater.autocorr(lag=i)
        # auto_corrs.append(auto_corr)

    # plot
    fig, ax = plt.subplots()
    ax.plot(lags, cross_corrs)
    # plot vline for maximum correlation. Check for which x value this is

    # print(crosscorr(groundwater, extensometer["0.05 m-mv"]))
