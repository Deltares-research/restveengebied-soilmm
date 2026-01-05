import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import dates as mdates
from pathlib import Path

# import cmocean
import re

from soilmm.read import (
    read_extensometer,
    read_groundwater,
    read_soilprofile,
    read_hydraulic_head,
    read_middepth_filter,
)
from soilmm.layer_analysis import calculate_layer_thickness
from soilmm.constants import LOCATION_FULLNAMES, SOILPROFILE_DEPTHS

from soilmm.reference_date_correction import subtract_value_in_januari
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
phreatic_head_data = read_groundwater(location)
aquifer_data = read_hydraulic_head(location)
# middepth_filter_data = read_middepth_filter(location)

soilprofile_lithology, soilprofile_anchors = read_soilprofile(location)

#################################################################
# levelling correction
#################################################################

reference_date, extensometer_data = subtract_value_in_januari(extensometer_data)

################################################################
# Correlation
################################################################

min_groundwater_level = np.min(phreatic_head_data) / 100 * -1 - 0.5

print(f"The deepest anchor height for cross correlations is {min_groundwater_level}")

lags = np.arange(-7 * 24 + 1, 1 * 24)
# lags = np.arange(-10, 10)

cross_corrs = {}

for anchor in extensometer_data:

    print(anchor)

    anchor_height = re.findall(r"\d+", anchor)

    # print(anchor_height)

    anchor_height = float(anchor_height[0]) / 100
    print(anchor_height)

    if anchor_height < min_groundwater_level:

        cross_corr_single_anchor = []
        # print(float(anchor)[:3]
        for lag in lags:
            # print(i)
            cross_corr = crosscorr(
                phreatic_head_data, extensometer_data[anchor], lag=lag
            )
            cross_corr_single_anchor.append(cross_corr)

        cross_corrs[anchor] = cross_corr_single_anchor

################################################################
# correlation bewtween deep and shallow groundwater filters
################################################################

lags = np.arange(-7 * 24 + 1, 1 * 24)

cross_corrs_deep_shallow = []
for lag in lags:
    cross_corr = crosscorr(phreatic_head_data, aquifer_data, lag=lag)
    cross_corrs_deep_shallow.append(cross_corr)

################################################################
# the plot
################################################################

fig, axs = plt.subplots(nrows=2, ncols=1)
# fig, axs = plt.subplots(nrows=3, ncols=2, gridspec_kw={"width_ratios": [4, 1]})

# some attributes
colors = plt.cm.viridis_r(np.linspace(0, 1, len(extensometer_data.columns)))
# colors = cmocean.cm.deep(np.linspace(0, 1, len(extensometer_data.columns)))
# colors = cmocean.cm.haline_r(np.linspace(0, 1, len(extensometer_data.columns)))

locator = mdates.AutoDateLocator(minticks=2, maxticks=6)
formatter = mdates.ConciseDateFormatter(locator)

# for j, column in enumerate(extensometer_data.columns):

#     extensometer_data_column = extensometer_data[column]

#     axs[0, 0].plot(
#         extensometer_data_column[extensometer_data_column.index <= levelling_date],
#         color=colors[j],
#         linewidth=0.7,
#         alpha=0.5,
#     )

#     axs[0, 0].plot(
#         extensometer_data_column[extensometer_data_column.index >= levelling_date],
#         label=column,
#         color=colors[j],
#         linewidth=0.7,
#     )

for i, column in enumerate(extensometer_data.columns):

    # layer_thickness_data_column = layer_thickness_data[column]

    # axs[2, 0].plot(
    #     layer_thickness_data_column[
    #         layer_thickness_data_column.index <= levelling_date
    #     ],
    #     color=colors[i + 1],
    #     linewidth=0.7,
    #     alpha=0.5,
    # )

    # axs[2, 0].plot(
    #     layer_thickness_data_column[
    #         layer_thickness_data_column.index >= levelling_date
    #     ],
    #     label=column,
    #     color=colors[i + 1],
    #     linewidth=0.7,
    # )

    column_height = re.findall(r"\d+", column)

    # column_height = column_height[0] + "." + column_height[1]
    column_height = float(column_height[0]) / 100

    if column_height < min_groundwater_level:

        correlation_data_column = cross_corrs[column]

        idxmax = np.argmax(cross_corrs[column])

        axs[1].plot(
            lags,
            correlation_data_column,
            label=column,
            color=colors[i],
            linewidth=0.7,
        )

        print(
            f"The lag with the maximum correlation coefficient for {column} is {lags[idxmax]}"
        )

        axs[1].axvline(x=lags[idxmax], color=colors[i], linewidth=0.9, linestyle="--")

axs[0].plot(
    phreatic_head_data[phreatic_head_data.index <= reference_date],
    color="blue",
    linewidth=0.7,
    zorder=1,
    alpha=0.5,
)

axs[0].plot(
    phreatic_head_data[phreatic_head_data.index >= reference_date],
    label="Shallow filter 'phreatic'",
    color="blue",
    linewidth=0.7,
    zorder=1,
)

axs[0].plot(
    aquifer_data[aquifer_data.index <= reference_date],
    color="deepskyblue",
    linewidth=0.7,
    zorder=1,
    alpha=0.5,
)

axs[0].plot(
    aquifer_data[aquifer_data.index >= reference_date],
    label="Deep filter 'aquifer'",
    color="deepskyblue",
    linewidth=0.7,
    zorder=1,
)

# for ax in axs[:].flat:
for ax in axs[:-1].flat:

    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    ax.grid()

    # vertical reference date line
    ax.axvline(
        x=pd.to_datetime(reference_date),
        color="black",
        linewidth=0.6,
        zorder=1,
    )

    ax.set_xlim(
        [extensometer_data.first_valid_index(), extensometer_data.last_valid_index()]
    )

axs[1].grid()

axs[0].legend(
    loc="upper center",
    bbox_to_anchor=(1.25, 0.85),
)
axs[1].legend(
    loc="upper center",
    bbox_to_anchor=(1.3, 0.85),
)
# axs[2].legend(
#     loc="upper center",
#     bbox_to_anchor=(0.2, -0.15),
# )

axs[0].set_title(f"Groundwater level", fontsize=10)
axs[1].set_title(f"Correlation", fontsize=10)

axs[0].set_ylabel(
    "Groundwater level relative\n to NAP [cm]",
)
axs[1].set_ylabel("Correlation coefficient")

axs[1].set_xlabel("Time lag (hours)")

###########################################
# other figure settings
###########################################

fig.set_figwidth(9 / 5 * 4)
fig.set_figheight(7)
plt.subplots_adjust(hspace=0.3, wspace=0.3)

fig.suptitle(location_fullname, fontweight="bold", y=0.94)

outputdir = Path(
    r"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging"
)
# plt.savefig(
#     outputdir.joinpath(
#         "data",
#         "4-visualisation",
#         location_fullname,
#         f"anchor_correlation.png",
#     ),
#     bbox_inches="tight",
#     dpi=300,
# )
plt.show()
