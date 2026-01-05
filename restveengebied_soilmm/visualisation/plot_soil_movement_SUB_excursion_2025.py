import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import dates as mdates
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.ticker as ticker
from pathlib import Path

from restveengebied_soilmm.read import (
    read_extensometer,
    read_groundwater,
    read_soilprofile,
    read_hydraulic_head,
    read_middepth_filter,
    read_surface_level,
)
from restveengebied_soilmm.layer_analysis import calculate_layer_thickness
from restveengebied_soilmm.constants import (
    LOCATION_FULLNAMES,
    SOILPROFILE_DEPTHS,
    SOILTYPES_COLORS,
)

from restveengebied_soilmm.old_scripts.stats import get_trendline

#################################################################
# Parameters
#################################################################

locations = ["ZEG"]
# locations = ["ALB", "ASD", "ROU", "ZEG", "VLI", "DEM", "LW", "VEG", "ZH"]
plot_type = "MP"
plot_names = {
    "RF": "Reference",
    "MP": "Pressurized subsurface infiltration",
    "MS": "Subsubsurface infiltration",
}
plot_name = plot_names[plot_type]

for location in locations:
    print(f"Plotting data for location: {location}")

    location_fullname = LOCATION_FULLNAMES[location]
    soilprofile_depth = SOILPROFILE_DEPTHS[location]

    #################################################################
    # read data
    #################################################################

    extensometer_data = read_extensometer(location, plot_type=plot_type)
    groundwater_data = read_groundwater(location, plot_type=plot_type)
    # hydraulic_head_data = read_hydraulic_head(location)
    # middepth_filter_data = read_middepth_filter(location)
    surface_level = read_surface_level(location, plot_type=plot_type)

    soilprofile_lithology, soilprofile_anchors = read_soilprofile(
        location, plot_type=plot_type
    )

    ################################################################
    # calculate layer thicknesses
    ################################################################

    layer_thickness_data = calculate_layer_thickness(extensometer_data)

    ################################################################
    # the plot
    ################################################################

    fig, axs = plt.subplots(nrows=3, ncols=2, gridspec_kw={"width_ratios": [4, 1]})

    # some plot attributes
    colors = plt.cm.viridis_r(np.linspace(0, 1, len(extensometer_data.columns)))
    locator = mdates.AutoDateLocator(minticks=2, maxticks=6)
    formatter = mdates.ConciseDateFormatter(locator)

    # plot the surface level
    axs[0, 0].text(
        1.28,
        1.05,
        f"Surface level: {surface_level:.0f} cm NAP",
        fontsize=10,
        fontweight="bold",
        ha="center",
        va="center",
        transform=axs[0, 0].transAxes,
    )

    plot_trendline = True

    for j, column in enumerate(extensometer_data.columns):

        extensometer_data_column = extensometer_data[column]

        axs[0, 0].plot(
            extensometer_data_column,
            label=column,
            color=colors[j],
            linewidth=0.7,
        )

        if plot_trendline:
            # if location == "LW":
            #     extensometer_data_column = extensometer_data_column.loc["2023":]

            p, x, r_2, slope = get_trendline(extensometer_data_column)

            axs[0, 0].plot(
                x,
                p(x),
                linestyle="--",
                color=colors[j],
                linewidth=0.7,
            )

    for i, column in enumerate(layer_thickness_data.columns):

        layer_thickness_data_column = layer_thickness_data[column]

        axs[1, 0].plot(
            layer_thickness_data_column,
            label=column,
            color=colors[i],
            linewidth=0.7,
        )

        if plot_trendline:
            # if location == "LW":
            #     layer_thickness_data_column = layer_thickness_data_column.loc["2023":]
            p, x, r_2, slope = get_trendline(layer_thickness_data_column)

            axs[1, 0].plot(
                x,
                p(x),
                linestyle="--",
                color=colors[i],
                linewidth=0.7,
            )

    axs[2, 0].plot(
        groundwater_data,
        label="Shallow filter 'phreatic'",
        color="deepskyblue",
        linewidth=0.7,
        zorder=1,
    )

    # if isinstance(middepth_filter_data, pd.Series):
    #     axs[2, 0].plot(
    #         middepth_filter_data,
    #         label="Mid-depth filter",
    #         color="royalblue",
    #         linewidth=0.7,
    #         zorder=1,
    #     )

    # axs[2, 0].plot(
    #     hydraulic_head_data,
    #     label="Deep filter 'aquifer'",
    #     color="darkblue",
    #     linewidth=0.7,
    #     zorder=1,
    # )

    for ax in axs[:, 0].flat:

        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        ax.grid()

        ax.set_xlim(
            [
                extensometer_data.first_valid_index(),
                extensometer_data.last_valid_index(),
            ]
        )

    axs[0, 0].legend(
        loc="upper center",
        bbox_to_anchor=(1.25, 0.85),
    )
    axs[1, 0].legend(
        loc="upper center",
        bbox_to_anchor=(1.3, 0.85),
    )
    axs[2, 0].legend(
        loc="upper center",
        bbox_to_anchor=(0.2, -0.15),
    )

    axs[0, 0].set_title(f"Anchor height", fontsize=10)
    axs[1, 0].set_title(f"Layer thickness", fontsize=10)
    axs[2, 0].set_title(f"Groundwater level", fontsize=10)

    axs[0, 0].set_ylabel(f"Change in height (cm)")
    axs[1, 0].set_ylabel(f"Change in thickness (cm)")
    axs[2, 0].set_ylabel(
        "Groundwater level relative\n to NAP [cm]",
    )

    axs[0, 1].axis("off")
    axs[1, 1].axis("off")

    match location:
        case "ZEG":
            axs[0, 0].set_ylim([-6, 6])
            axs[1, 0].set_ylim([-5, 5])
        case _:
            axs[0, 0].set_ylim([-6, 6])
            axs[1, 0].set_ylim([-2.5, 2.5])

    match location:
        case "ALB":
            axs[2, 0].set_ylim([-245, -95])
        case "ASD":
            axs[2, 0].set_ylim([-305, -155])
        case "ROU":
            axs[2, 0].set_ylim([-185, -35])
        case "VLI":
            axs[2, 0].set_ylim([-300, -150])
        case "ZEG":
            axs[2, 0].set_ylim([-365, -235])
        case "ZH":
            axs[2, 0].set_ylim([-365, -215])
        case "VEG":
            axs[2, 0].set_ylim([-280, -130])
        case "LAW":
            axs[2, 0].set_ylim([-320, -170])
        case "DEM":
            axs[2, 0].set_ylim([-340, -190])

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

    fig.suptitle(
        f"{location_fullname} {plot_name}",
        fontweight="bold",
        y=0.94,
        x=0.6,
        ha="center",
    )

    outputdir = Path(
        r"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging"
    )
    plt.savefig(
        outputdir.joinpath(
            "data",
            "5-visualisation",
            location_fullname,
            f"soil_movement_SUB_excursion_2025_{plot_type}.png",
        ),
        bbox_inches="tight",
        dpi=300,
    )
    # plt.show()
