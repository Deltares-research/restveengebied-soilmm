from pathlib import Path
from collections import OrderedDict

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

from restveengebied_soilmm.read import read_soilprofile, read_strain
from restveengebied_soilmm.constants import (
    LOCATION_FULLNAMES,
    SOILPROFILE_DEPTHS,
    SOILTYPES_COLORS,
)


def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)


mpl.rcParams["xtick.top"] = True
mpl.rcParams["xtick.labeltop"] = True
mpl.rcParams["xtick.bottom"] = False
mpl.rcParams["xtick.labelbottom"] = False


locations = ["ZEG"]

width_soil = 2
width_strain = 3

soiltypes_at_nobv_locations_for_legend = [
    "clay",
    "peat",
    "peat, clayey",
    "sand",
    "sand, mixed \nwith clay and/or silt",
    "sand/loam",
    "loam/sand",
]

# see this link for adding a parasite axis: https://stackoverflow.com/questions/20146652/two-y-axis-on-the-left-side-of-the-figure


# fig, axs = plt.subplots(
#     nrows=2,
#     ncols=6,
#     sharey=True,
#     gridspec_kw={
#         "width_ratios": [width_soil, width_strain] * 3
#     },  # 3 is the amount of locations on one row
#     figsize=(6.4 * 3 / 1.5, 9.6),
#     squeeze=False,
# )

for i, location in enumerate(locations):

    location_fullname = LOCATION_FULLNAMES[location]
    print(f"Plotting data for location: {location_fullname}")

    soilprofile_depth = SOILPROFILE_DEPTHS[location]
    soilprofile_lithology, soilprofile_anchors = read_soilprofile(
        location, location_fullname
    )

    path_stats = r"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging/data/4-output/trendlijn_statistieken.xlsx"

    strain = read_strain(path_stats, sheetname=location_fullname)

    ########################
    # the soil profile plot
    ########################

    fig, axs = plt.subplots(
        nrows=1,
        ncols=1,
        sharey=True,
        squeeze=False,
        figsize=((6.4 * 2) / (1.5 * 5), 4.8),
    )

    # plot the anchor depths
    for anchor in soilprofile_anchors["m-mv"]:
        axs[0, i].hlines(anchor * -1, -1, 1, color="black", zorder=2)

        axs[0, i].plot(
            0.44, anchor * -1, "<", color="black", markersize=5, clip_on=False
        )

    # plot the bars
    for lith in soilprofile_lithology.iterrows():
        axs[0, i].bar(
            "Soil \n composition",
            lith[1]["dikte"] / 100,
            bottom=lith[1]["bovengrens [cm]"] / 100,
            label=lith[0],
            color=SOILTYPES_COLORS[lith[0]],
            zorder=1,
        )

    axs[0, i].set_xlim([-0.4, 0.4])
    # axs[row, i].set_ylim(0, SOILPROFILE_DEPTHS["ASD"])

    axs[0, i].get_xaxis().set_ticks([])  # this turns off the text at the top of the bar

    axs[0, i].text(
        x=0.5,
        y=1.03,
        s=location_fullname + "\n" + "Reference",
        fontsize=14,
        transform=axs[0, i].transAxes,
        horizontalalignment="center",
    )

    axs[0, i].tick_params(axis="both", which="major", labelsize=12)

    ########################
    # the second axes
    ########################

    # axs[0, i + 1].set_xlabel("mm/yr/m", fontsize=12)
    # axs[0, i + 1].xaxis.set_label_position("top")
    # axs[0, i + 1].xaxis.label.set_color("red")

    # axs[0, i + 1].vlines(
    #     strain["Strain"] * 1000,
    #     strain["upper bounds"] / 100,
    #     strain["lower bounds"] / 100,
    #     color="red",
    # )

    # axs[0, i + 1].spines["right"].set_visible(False)
    # axs[0, i + 1].spines["bottom"].set_visible(False)
    # axs[0, i + 1].spines["left"].set_zorder(1)

    # axs[0, i + 1].set_xlim([-15, 0.75])
    # axs[0, i + 1].set_xticks([-15, -7.5, 0])

    # axs[0, i + 1].spines["left"].set_position("zero")

    # axs[0, i + 1].tick_params(axis="both", which="major", labelsize=12)

    # ########################
    # # the parasite axis
    # ########################
    # par = axs[0, i + 1].twiny()
    # par.spines["top"].set_position(("axes", 1.2))

    # make_patch_spines_invisible(par)
    # par.spines["top"].set_visible(True)
    # par.xaxis.set_label_position("top")
    # par.xaxis.set_ticks_position("top")

    # par.set_xlabel("c (%)", fontsize=12)
    # par.set_xlim([-5, 100])
    # par.vlines(
    #     strain["Contribution to subsidence (%).1"],
    #     strain["upper bounds"] / 100,
    #     strain["lower bounds"] / 100,
    #     color="dodgerblue",
    #     zorder=3,
    # )
    # par.xaxis.label.set_color("dodgerblue")
    # par.tick_params(axis="x", colors="dodgerblue")
    # par.tick_params(axis="both", which="major", labelsize=12)

    # axs[0, i + 1].tick_params(axis="x", colors="red")
    # axs[0, i + 1].tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)

    ########################
    # plot a legend in the bottom right corner
    ########################

    # if (row == 1) & (i == 1):

    # handles = []

    # for soiltype, color in SOILTYPES_COLORS.items():
    #     if soiltype in soiltypes_at_nobv_locations_for_legend:
    #         handles.append(mpatches.Patch(color=color, label=soiltype))

    handles, labels = axs[0, i].get_legend_handles_labels()

    # this to add a triangle symbol for the anchors to the legend
    point = Line2D(
        [0],
        [0],
        label="anchor",
        marker="<",
        markersize=10,
        color="k",
        linestyle="",
    )

    handles.extend([point])
    labels.extend([point._label])

    by_label = OrderedDict(zip(labels, handles))

    if location in ["ZEG"]:
        key_order = [
            "clay",
            "peat",
            "peat, clayey",
            "sand",
            "sand, mixed \nwith clay and/or silt",
            "anchor",
        ]
        for k in key_order:  # a loop to force the order you want
            by_label.move_to_end(k)

    soilprofile_legend = axs[0, i].legend(
        by_label.values(),
        by_label.keys(),
        bbox_to_anchor=(2.05, 0.95),
        loc="upper center",
        frameon=False,
        fontsize=12,
        ncol=1,
        title="Soil types:",
        title_fontsize=14,
        alignment="left",
    )

    # this sets the whitespace between the legend title and the legend entries
    soilprofile_legend._legend_box.sep = 12

    axs[0, i].invert_yaxis()
    # axs[0, i + 1].invert_xaxis()

    axs[0, 0].set_ylabel("m below surface level", fontsize=12)
    # axs[1, 0].set_ylabel("m below surface level", fontsize=12)

    # axs[1, -1].set_visible(False)
    # axs[1, -2].set_visible(False)

    fig.subplots_adjust(hspace=0.48)

    outputdir = Path(
        r"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging"
    )

    plt.savefig(
        outputdir.joinpath(
            "data",
            "5-visualisation",
            location_fullname,
            "soil_profile.png",
        ),
        bbox_inches="tight",
        dpi=300,
    )
