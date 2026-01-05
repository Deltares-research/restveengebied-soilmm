import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import dates as mdates
from pathlib import Path

# import cmocean
import re

from read import (
    read_extensometer,
    read_groundwater,
    read_soilprofile,
    read_hydraulic_head,
    read_middepth_filter,
)
from soilmm.layer_analysis import calculate_layer_thickness
from soilmm.constants import LOCATION_FULLNAMES, SOILPROFILE_DEPTHS, SOILTYPES_COLORS
from soilmm.correlation import crosscorr

#################################################################
# Parameters
#################################################################

location = "ALB"
location_fullname = LOCATION_FULLNAMES[location]
soilprofile_depth = SOILPROFILE_DEPTHS[location]

#################################################################
# read data
#################################################################

extensometer_data = read_extensometer(location)
groundwater_data = read_groundwater(location)
hydraulic_head_data = read_hydraulic_head(location)
middepth_filter_data = read_middepth_filter(location)

soilprofile_lithology, soilprofile_anchors = read_soilprofile(location)

################################################################
# calculate layer thicknesses
################################################################

layer_thickness_data = calculate_layer_thickness(extensometer_data)

################################################################
# Correlation
################################################################

min_groundwater_level = np.min(groundwater_data) * -1 - 50

print(f"The deepest anchor height for cross correlations is {min_groundwater_level}")

lags = np.arange(-7 * 24 + 1, 1 * 24)
# lags = np.arange(-10, 10)

cross_corrs = {}

for anchor in extensometer_data:

    print(anchor)

    anchor_height = re.findall(r"\d+", anchor)

    anchor_height = anchor_height[0]  # + "." + anchor_height[1]

    if float(anchor_height) < min_groundwater_level:

        print(f"Anchor {anchor} is above the groundwater level")

        cross_corr_single_anchor = []
        for lag in lags:
            cross_corr = crosscorr(groundwater_data, extensometer_data[anchor], lag=lag)
            cross_corr_single_anchor.append(cross_corr)

        cross_corrs[anchor] = cross_corr_single_anchor

################################################################
# the plot
################################################################

fig, axs = plt.subplots(nrows=3, ncols=2, gridspec_kw={"width_ratios": [4, 1]})

# some attributes
colors = plt.cm.viridis_r(np.linspace(0, 1, len(extensometer_data.columns)))
# colors = cmocean.cm.deep(np.linspace(0, 1, len(extensometer_data.columns)))
# colors = cmocean.cm.haline_r(np.linspace(0, 1, len(extensometer_data.columns)))

locator = mdates.AutoDateLocator(minticks=2, maxticks=6)
formatter = mdates.ConciseDateFormatter(locator)

for j, column in enumerate(extensometer_data.columns):

    extensometer_data_column = extensometer_data[column]

    axs[0, 0].plot(
        extensometer_data_column,
        label=column,
        color=colors[j],
        linewidth=0.7,
    )

for i, column in enumerate(extensometer_data.columns):

    column_height = re.findall(r"\d+", column)

    column_height = column_height[0]  #  + "." + column_height[1]

    if float(column_height) < min_groundwater_level:

        correlation_data_column = cross_corrs[column]

        idxmax = np.argmax(cross_corrs[column])

        axs[2, 0].plot(
            lags,
            correlation_data_column,
            label=column,
            color=colors[i],
            linewidth=0.7,
        )

        print(
            f"The lag with the maximum correlation coefficient for {column} is {lags[idxmax]}"
        )

        axs[2, 0].axvline(
            x=lags[idxmax], color=colors[i], linewidth=0.9, linestyle="--"
        )


axs[1, 0].plot(
    groundwater_data,
    label="Shallow filter 'phreatic'",
    color="deepskyblue",
    linewidth=0.7,
    zorder=1,
)

axs[1, 0].plot(
    hydraulic_head_data,
    label="Deep filter 'aquifer'",
    color="darkblue",
    linewidth=0.7,
    zorder=1,
)

if isinstance(middepth_filter_data, pd.Series):
    axs[1, 0].plot(
        middepth_filter_data,
        label="Mid-depth filter",
        color="royalblue",
        linewidth=0.7,
        zorder=1,
    )

for ax in axs[:-1, 0].flat:

    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    ax.grid()

    ax.set_xlim(
        [extensometer_data.first_valid_index(), extensometer_data.last_valid_index()]
    )

axs[2, 0].grid()

axs[0, 0].legend(
    loc="upper center",
    bbox_to_anchor=(1.25, 0.85),
)
axs[1, 0].legend(
    loc="upper center",
    bbox_to_anchor=(1.3, 0.85),
)

axs[0, 0].set_title(f"Anchor height", fontsize=10)
axs[1, 0].set_title(f"Groundwater level", fontsize=10)
axs[2, 0].set_title(f"Correlation", fontsize=10)

axs[0, 0].set_ylabel(f"Change in height \n(cm)")
axs[1, 0].set_ylabel(
    "Groundwater level relative\n to NAP [cm]",
)
axs[2, 0].set_ylabel("Correlation coefficient")

axs[2, 0].set_xlabel("Time lag (hours)")

axs[0, 1].axis("off")
axs[1, 1].axis("off")

############################################
# plot the soil profile
############################################

for anchor in soilprofile_anchors["m-mv"]:
    axs[2, 1].hlines(anchor * 100 * -1, -1, 1, color="black", zorder=2)

    axs[2, 1].plot(
        0.44, anchor * 100 * -1, "<", color="black", markersize=5, clip_on=False
    )

for lith in soilprofile_lithology.iterrows():
    axs[2, 1].bar(
        "Soil composition",
        lith[1]["dikte"],
        bottom=lith[1]["bovengrens [cm]"],
        label=lith[0],
        color=SOILTYPES_COLORS[lith[0]],
        zorder=1,
    )

axs[2, 1].set_xlim([-0.4, 0.4])
axs[2, 1].set_ylabel("cm below surface level")
axs[2, 1].set_ylim(0, soilprofile_depth * 100)

handles, labels = axs[2, 1].get_legend_handles_labels()

by_label = dict(zip(labels, handles))

soilprofile_legend = axs[2, 1].legend(
    by_label.values(),
    by_label.keys(),
    bbox_to_anchor=(1.85, 0.95),
    loc="upper center",
    frameon=False,
    fontsize=9,
    ncol=1,
    title="Soil types:",
)

axs[2, 1].invert_yaxis()

###########################################
# other figure settings
###########################################

fig.set_figwidth(9)
fig.set_figheight(10.5)
plt.subplots_adjust(hspace=0.3, wspace=0.3)

fig.suptitle(location_fullname, fontweight="bold", y=0.94)

outputdir = Path(
    r"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging"
)
plt.savefig(
    outputdir.joinpath(
        "data",
        "5-visualisation",
        location_fullname,
        f"anchor_correlation.png",
    ),
    bbox_inches="tight",
    dpi=300,
)
# plt.show()
