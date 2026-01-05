import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import dates as mdates
from collections import OrderedDict
from pathlib import Path

import cmocean

from restveengebied_soilmm.read import (
    read_extensometer,
    read_soilprofile,
    read_soilprofile_regiodeal,
    read_ditch_level,
    read_surface_level,
    read_gwlevel,
    read_filter_depths,
)
from restveengebied_soilmm.layer_analysis import calculate_layer_thickness
from restveengebied_soilmm.constants import (
    LOCATION_FULLNAMES,
    SOILPROFILE_DEPTHS,
    SOILTYPES_COLORS_DUTCH,
)

from restveengebied_soilmm.old_scripts.stats import get_trendline

#################################################################
# Parameters
#################################################################

# locations = ["HZW"]  # "BKG"]  #
# locations = ["ALB", "ASD", "ROU", "ZEG", "VLI", "DEM", "LW", "VEG", "ZH"]
# locations = ["ZEG"]
locations = ["M4T", "MMW", "MSW"]
# locations = ["MMW"]
# locations = ["VEG"]
plot_type = "RF"
plot_names = {
    "RF": "Reference",
    "MP": "Pressurized subsurface infiltration",
    "MS": "Subsubsurface infiltration",
}
plot_name = plot_names[plot_type]

trendline_months = (1, 2)

for location in locations:

    location_fullname = LOCATION_FULLNAMES[location]
    print(f"Plotting data for location: {location_fullname}")

    #################################################################
    # read data
    #################################################################

    if location in SOILPROFILE_DEPTHS.keys():
        soilprofile_depth = SOILPROFILE_DEPTHS[location]
        if location in [
            "ALB",
            "ASD",
            "ROU",
            "VLI",
            "ZEG",
            "DEM",
            "LW",
            "VEG",
            "ZH",
            "BKW",
            "BKG",
            "CBW",
            "HZW",
            "ROU09",
            "M4T",
            "MMW",
            "MSW",
        ]:
            soilprofile_lithology, soilprofile_anchors = read_soilprofile(
                location, location_fullname, plot_type=plot_type, language="dutch"
            )
        elif location in ["GDA"]:
            soilprofile_lithology, soilprofile_anchors = read_soilprofile_regiodeal(
                location, location_fullname
            )

    extensometer_data = read_extensometer(location, plot_type=plot_type)
    groundwater_data = read_gwlevel(location, plot_type=plot_type)
    ditch_level_data = read_ditch_level(location, plot_type=plot_type)
    surface_level = read_surface_level(location, plot_type=plot_type)

    try:
        filter_depths = read_filter_depths(location, plot_type=plot_type)
        filter_depths_mv = surface_level - filter_depths

    except FileNotFoundError:
        print("The filter depths are not found")

    ditch_level_data = ditch_level_data.loc[
        extensometer_data.first_valid_index() : extensometer_data.last_valid_index()
    ]

    match location:
        case "MSW":
            extensometer_data.loc["2025-11-15":] = np.nan

    ################################################################
    # calculate layer thicknesses
    ################################################################

    layer_thickness_data = calculate_layer_thickness(extensometer_data)

    ################################################################
    # rename anchor depths for legend
    ################################################################

    extensometer_data.columns = extensometer_data.columns.str.replace(
        " bs", "-mv", regex=True
    )

    layer_thickness_data.columns = layer_thickness_data.columns.str.replace(
        " bs", "-mv", regex=True
    )
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
        1.15,
        f"Maaiveldhoogte: {surface_level:.0f} cm NAP",
        fontsize=10,
        fontweight="bold",
        ha="center",
        va="center",
        transform=axs[0, 0].transAxes,
    )

    plot_trendline = False

    print(
        f"The extensometer depths for {location} are: {extensometer_data.columns.to_list()}"
    )

    for j, column in enumerate(extensometer_data.columns):

        # optional, uncomment the two lines below to skip plotting an anchor entirely (also does not plot a trendline)
        # if column.isin(["6 cm bs"]):
        #     continue

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

            if location in ["BKG"]:
                extensometer_data_column_1 = extensometer_data_column.loc[:"2023-09-15"]
                extensometer_data_column_2 = extensometer_data_column.loc["2023-11-05":]

                extensometer_data_column_1.name = f"{column}_1"
                extensometer_data_column_2.name = f"{column}_2"

                extensometer_data_columns = pd.concat(
                    [extensometer_data_column_1, extensometer_data_column_2],
                    axis="columns",
                )
            else:
                extensometer_data_columns = extensometer_data_column.to_frame()

            for column in extensometer_data_columns:
                p, x, r_2, slope = get_trendline(
                    extensometer_data_columns[column].dropna(), months=trendline_months
                )

                print(f"The slope of the anchor at {column} is {slope} cm/yr.")

                axs[0, 0].plot(
                    x,
                    p(x),
                    linestyle="--",
                    color=colors[j],
                    linewidth=0.7,
                )

    print(
        f"The layer thicknesses calculated for {location} are: {layer_thickness_data.columns.to_list()}"
    )

    for i, column in enumerate(layer_thickness_data.columns):

        # optional, this skip plotting the anchor entirely (also does not plot a trendline)
        # if column.isin(["41 cm bs - 6 cm bs"]):
        #     continue

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

            if location in ["BKG"]:
                layer_thickness_data_column_1 = layer_thickness_data_column.loc[
                    :"2023-09-15"
                ]
                layer_thickness_data_column_2 = layer_thickness_data_column.loc[
                    "2023-11-05":
                ]

                layer_thickness_data_column_1.name = f"{column}_1"
                layer_thickness_data_column_2.name = f"{column}_2"

                layer_thickness_data_columns = pd.concat(
                    [layer_thickness_data_column_1, layer_thickness_data_column_2],
                    axis="columns",
                )
            else:
                layer_thickness_data_columns = layer_thickness_data_column.to_frame()

            for column in layer_thickness_data_columns:
                p, x, r_2, slope = get_trendline(
                    layer_thickness_data_columns[column].dropna(),
                    months=trendline_months,
                )

                print(f"The slope of the layer thickness {column} is {slope} cm/yr.")

                axs[1, 0].plot(
                    x,
                    p(x),
                    linestyle="--",
                    color=colors[i],
                    linewidth=0.7,
                )

    # colors_gw = plt.cm.winter_r(np.linspace(0, 1, len(groundwater_data.columns)))
    # colors_gw = plt.cm.cool(np.linspace(0, 1, len(groundwater_data.columns)))
    cmap = plt.cm.Blues
    # # cmap = plt.cm.BuPu
    # # cmap = plt.cm.plasma
    newcmap = cmocean.tools.crop_by_percent(cmap, 40, which="min", N=None)

    match location:
        case "MMW" | "MSW":
            colors_gw = ["#90e0ef", "#00b4d8", "#0077b6", "#03045e"]
        case "M4T":
            colors_gw = ["#90e0ef", "#00b4d8", "#03045e"]

    # colors_gw = newcmap(np.linspace(0, 1, len(groundwater_data.columns)))

    for i, well in enumerate(groundwater_data):
        top_filter = filter_depths_mv.iloc[i].values[0]
        bottom_filter = filter_depths_mv.iloc[i].values[-1]
        axs[2, 0].plot(
            groundwater_data[well],
            label=f"filter diepte: {bottom_filter:.0f} - {top_filter:.0f} cm-mv",
            color=colors_gw[i],
            linewidth=0.7,
            zorder=1,
        )

    if not all(pd.isna(ditch_level_data)):
        axs[2, 0].plot(
            ditch_level_data,
            label="Slootpeil",
            color="blueviolet",
            linewidth=0.7,
            zorder=1,
            # alpha=0.5,
        )

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

    handles_ax2, labels_ax2 = axs[2, 0].get_legend_handles_labels()

    axs[0, 0].legend(
        loc="upper center",
        bbox_to_anchor=(1.25, 0.85),
    )
    axs[1, 0].legend(
        loc="upper center",
        bbox_to_anchor=(1.3, 0.85),
    )

    if handles_ax2:
        axs[2, 0].legend(
            loc="upper center",
            bbox_to_anchor=(0.45, -0.20),
        )

    axs[0, 0].set_title("Verticale beweging ankers", fontsize=10)
    axs[1, 0].set_title("Laagdikteverandering", fontsize=10)
    axs[2, 0].set_title("Waterdruk", fontsize=10)

    axs[0, 0].set_ylabel("Hoogteverandering t.o.v. T0 (cm)")
    axs[1, 0].set_ylabel("Laagdikteverandering t.o.v. T0 (cm)")
    axs[2, 0].set_ylabel(
        "Grondwaterstand (cm NAP)",
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
            axs[2, 0].set_ylim([-365, -215])
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

    if location in SOILPROFILE_DEPTHS.keys():
        for anchor in soilprofile_anchors["m-mv"]:
            axs[2, 1].hlines(anchor * 100 * -1, -1, 1, color="black", zorder=2)

            axs[2, 1].plot(
                0.44, anchor * 100 * -1, "<", color="black", markersize=5, clip_on=False
            )

        if not soilprofile_lithology.empty:
            for lith in soilprofile_lithology.iterrows():
                axs[2, 1].bar(
                    "Bodemopbouw",
                    lith[1]["dikte"],
                    bottom=lith[1]["bovengrens [cm]"],
                    label=lith[0],
                    color=SOILTYPES_COLORS_DUTCH[lith[0]],
                    zorder=1,
                )

        axs[2, 1].set_ylim(0, soilprofile_depth * 100)

        handles, labels = axs[2, 1].get_legend_handles_labels()

        # by_label = dict(zip(labels, handles))
        by_label = OrderedDict(zip(labels, handles))

        if location in ["GOU"]:
            key_order = ["sand", "organic sand", "clay", "organic clay", "peat"]
            for k in key_order:  # a loop to force the order you want
                by_label.move_to_end(k)
        if location in ["M4T"]:
            # key_order = ["clay", "organic clay", "peat", "peat, clayey", "sand"]
            key_order = ["klei", "klei, humeus", "veen", "veen, kleiig", "zand"]
            for k in key_order:  # a loop to force the order you want
                by_label.move_to_end(k)
        if location in ["MMW"]:
            # key_order = ["clay", "organic clay", "peat", "gyttja", "sand"]
            key_order = ["klei", "klei, humeus", "veen", "gyttja", "zand"]
            for k in key_order:  # a loop to force the order you want
                by_label.move_to_end(k)
        if location in ["MSW"]:
            # key_order = ["clay", "peat", "peat, clayey", "gyttja", "sand"]
            key_order = ["klei", "veen", "veen, kleiig", "gyttja", "zand"]
            for k in key_order:  # a loop to force the order you want
                by_label.move_to_end(k)

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

    axs[2, 1].set_xlim([-0.4, 0.4])
    axs[2, 1].set_ylabel("cm-mv")

    ###########################################
    # other figure settings
    ###########################################

    fig.set_figwidth(9)
    fig.set_figheight(10.5)
    plt.subplots_adjust(hspace=0.3, wspace=0.3)

    match location:
        case (
            "DEM"
            | "LW"
            | "VEG"
            | "ZH"
            | "GDA"
            | "BKW"
            | "BKG"
            | "CBW"
            | "HZW"
            | "MMW"
            | "M4T"
            | "MSW"
        ):
            suptitle_name = location_fullname
        case _:
            suptitle_name = f"{location_fullname} {plot_name}"

    fig.suptitle(
        suptitle_name,
        fontweight="bold",
        y=0.94,
        x=0.6,
        ha="center",
    )

    outputdir = Path(
        r"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging"
    )

    match location:
        case (
            "DEM"
            | "LW"
            | "VEG"
            | "ZH"
            | "GDA"
            | "BKW"
            | "BKG"
            | "CBW"
            | "HZW"
            | "M4T"
            | "MMW"
            | "MSW"
        ):
            plot_type = ""
        case _:
            plot_type = "_" + plot_type

    plt.savefig(
        outputdir.joinpath(
            "data",
            "5-visualisation",
            location_fullname,
            f"soil_movement{plot_type}_Nederlands.png",
        ),
        bbox_inches="tight",
        dpi=300,
    )
    # plt.show()
