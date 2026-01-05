import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import dates as mdates
from pathlib import Path
# import cmocean
from statsmodels.tsa.seasonal import seasonal_decompose

from read import (
    read_extensometer,
    read_groundwater,
    read_soilprofile,
    read_hydraulic_head,
    read_middepth_filter,
    read_precipitation_deficit,
)
from layer_analysis import calculate_layer_thickness, detrend_layers
from constants import LOCATION_FULLNAMES, LEVELLING_DATES, SOILPROFILE_DEPTHS
from levelling_correction import subtract_value_at_levelling_date
from correlation import crosscorr

#################################################################
# Parameters
#################################################################

location = "ZEG"
location_fullname = LOCATION_FULLNAMES[location]
levelling_date = LEVELLING_DATES[location]
soilprofile_depth = SOILPROFILE_DEPTHS[location]

#################################################################
# read data
#################################################################

extensometer_data = read_extensometer(location)
precip_deficit_data = read_precipitation_deficit(location)

soilprofile_lithology, soilprofile_anchors = read_soilprofile(location)

#################################################################
# levelling correction
#################################################################

extensometer_data = subtract_value_at_levelling_date(extensometer_data, levelling_date)

################################################################
# calculate layer thicknesses
################################################################

layer_thickness_data = calculate_layer_thickness(extensometer_data)
layer_thickness_data_detrended = detrend_layers(
    layer_thickness_data, detrend_method="linear"
)

################################################################
# Correlation
################################################################

lags = np.arange(-28 * 24 + 1, 28 * 24)

cross_corrs = {}

for anchor in layer_thickness_data:
    cross_corr_single_anchor = []
    # print(float(anchor)[:3]

    for lag in lags:
        # print(i)
        cross_corr = crosscorr(
            precip_deficit_data, layer_thickness_data[anchor], lag=lag
        )
        cross_corr_single_anchor.append(cross_corr)

    cross_corrs[anchor] = cross_corr_single_anchor

################################################################
# the plot
################################################################

# fig, axs = plt.subplots(nrows=3, ncols=1)
fig, axs = plt.subplots(nrows=2, ncols=2, gridspec_kw={"width_ratios": [4, 1]})

# some attributes
colors = plt.cm.viridis_r(np.linspace(0, 1, len(extensometer_data.columns)))
# colors = cmocean.cm.deep(np.linspace(0, 1, len(extensometer_data.columns)))
# colors = cmocean.cm.haline_r(np.linspace(0, 1, len(extensometer_data.columns)))

locator = mdates.AutoDateLocator(minticks=2, maxticks=6)
formatter = mdates.ConciseDateFormatter(locator)

column = "9.30 m bs - 4.49 m bs"  # "0.41 m bs - 0.06 m bs"

layer_thickness_data_column = layer_thickness_data_detrended[column]
layer_thickness_data_column_no_seasonal_cycle = seasonal_decompose(
    layer_thickness_data_column, model="additive", period=365 * 24
).resid

axs[0, 0].plot(
    layer_thickness_data_column_no_seasonal_cycle[
        layer_thickness_data_column.index <= levelling_date
    ],
    color="grey",
    linewidth=0.7,
    alpha=0.5,
)

axs[0, 0].plot(
    layer_thickness_data_column_no_seasonal_cycle[
        layer_thickness_data_column.index >= levelling_date
    ],
    label=column,
    color="grey",
    linewidth=0.7,
)

layer_thickness_data_column_shifted = layer_thickness_data_column.shift(885)

axs[0, 0].plot(
    layer_thickness_data_column_shifted[
        layer_thickness_data_column.index >= levelling_date
    ],
    label=f"{column}_shifted",
    color=colors[0],
    linewidth=0.7,
)
axs[0, 0].plot(
    layer_thickness_data_column_shifted[
        layer_thickness_data_column.index <= levelling_date
    ],
    color=colors[0],
    linewidth=0.7,
    alpha=0.5,
)

correlation_data_column = cross_corrs[column]

idxmin = np.argmin(cross_corrs[column])

axs[1, 0].plot(
    lags,
    correlation_data_column,
    label=column,
    color=colors[0],
    linewidth=0.7,
)

axs[1, 0].axvline(x=lags[idxmin], color=colors[0], linewidth=0.9, linestyle="--")

axs_twin = axs[0, 0].twinx()
(p1,) = axs_twin.plot(
    precip_deficit_data,
    color="royalblue",
    linewidth=0.7,
    zorder=1,
)

axs_twin.yaxis.label.set_color(p1.get_color())
axs_twin.tick_params(axis="y", labelcolor=p1.get_color())

for ax in axs[:-1, 0].flat:

    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    ax.grid()

    # vertical reference date line
    ax.axvline(
        x=pd.to_datetime(levelling_date),
        color="black",
        linewidth=0.6,
        zorder=1,
    )

    ax.set_xlim(
        [extensometer_data.first_valid_index(), extensometer_data.last_valid_index()]
    )

axs[1, 0].grid()

axs[0, 0].legend(
    loc="upper center",
    bbox_to_anchor=(1.4, 0.85),
)

axs[1, 0].set_title(f"Correlation", fontsize=10)

axs[0, 0].set_ylabel(f"Change in thickness \n relative to {levelling_date} (cm)")
axs_twin.set_ylabel(
    "Precipitation deficit (mm)",
)
axs[1, 0].set_ylabel("Correlation coefficient")

axs[1, 0].set_xlabel("Time lag (hours)")

axs[0, 1].axis("off")

axs[0, 0].set_ylim(-1.65, 1.65)
axs_twin.set_ylim(-400, 400)

############################################
# plot the soil profile
############################################

soilprofile_colors = {
    "clay": "lawngreen",
    "klei, humeus": "yellowgreen",
    "peat": "sienna",
    "peat, clayey": "darkgoldenrod",
    "sand": "gold",
    "zand/leem": "orange",
    "leem/zand": "darkorange",
}

for anchor in soilprofile_anchors["m-mv"]:
    axs[1, 1].hlines(anchor, -1, 1, color="black", zorder=2)

for lith in soilprofile_lithology.iterrows():
    axs[1, 1].bar(
        "Soil composition",
        lith[1]["dikte"],
        bottom=lith[1]["bovengrens [cm]"],
        label=lith[0],
        color=soilprofile_colors[lith[0]],
        zorder=1,
    )

axs[1, 1].set_xlim([-0.4, 0.4])
axs[1, 1].set_ylabel("m below surface level")
axs[1, 1].set_ylim(soilprofile_depth, 0)

handles, labels = axs[1, 1].get_legend_handles_labels()

by_label = dict(zip(labels, handles))

axs[1, 1].legend(
    by_label.values(),
    by_label.keys(),
    bbox_to_anchor=(1.6, 0.95),
    loc="upper center",
    frameon=False,
    fontsize=9,
    ncol=1,
    title="Soil types:",
)

###########################################
# other figure settings
###########################################

fig.set_figwidth(9)
fig.set_figheight(7)
plt.subplots_adjust(hspace=0.3, wspace=0.3)

fig.suptitle(location_fullname, fontweight="bold", y=0.94)

outputdir = Path(
    r"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging"
)
plt.savefig(
    outputdir.joinpath(
        "data",
        "4-visualisation",
        location_fullname,
        f"thickness_weather_correlation_{column}.png",
    ),
    bbox_inches="tight",
    dpi=300,
)
# plt.show()
