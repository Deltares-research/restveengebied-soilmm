from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

from nobv_soilmm.read import read_soilprofile, read_strain
from nobv_soilmm.constants import (
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


locations = ["ZEG", "ROU", "ALB", "VLI", "ASD"]

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


fig, axs = plt.subplots(
    nrows=2,
    ncols=6,
    sharey=True,
    gridspec_kw={
        "width_ratios": [width_soil, width_strain] * 3
    },  # 3 is the amount of locations on one row
    figsize=(6.4 * 3 / 1.5, 9.6),
    squeeze=False,
)

for i, location in enumerate(locations):

    location_fullname = LOCATION_FULLNAMES[location]
    print(f"Plotting data for location: {location_fullname}")

    soilprofile_depth = SOILPROFILE_DEPTHS[location]
    soilprofile_lithology, soilprofile_anchors = read_soilprofile(
        location, location_fullname
    )

    path_stats = r"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging/data/4-output/trendlijn_statistieken.xlsx"

    strain = read_strain(path_stats, sheetname=location_fullname)

    if i < 3:
        row = 0
    else:
        row = 1
        i = i - 3

    ########################
    # the soil profile plot
    ########################

    # plot the anchor depths
    for anchor in soilprofile_anchors["m-mv"]:
        axs[row, (2 * i)].hlines(anchor * -1, -1, 1, color="black", zorder=2)

        axs[row, (2 * i)].plot(
            0.44, anchor * -1, "<", color="black", markersize=5, clip_on=False
        )

    # plot the bars
    for lith in soilprofile_lithology.iterrows():
        axs[row, (i * 2)].bar(
            "Soil \n composition",
            lith[1]["dikte"] / 100,
            bottom=lith[1]["bovengrens [cm]"] / 100,
            label=lith[0],
            color=SOILTYPES_COLORS[lith[0]],
            zorder=1,
        )

    axs[row, (i * 2)].set_xlim([-0.4, 0.4])
    axs[row, (i * 2)].set_ylim(0, SOILPROFILE_DEPTHS["ASD"])

    axs[row, (i * 2)].get_xaxis().set_ticks(
        []
    )  # this turns off the text at the top of the bar

    axs[row, (i * 2)].text(
        x=1.05,
        y=1.35,
        s=location_fullname,
        fontsize=14,
        transform=axs[row, (i * 2)].transAxes,
        horizontalalignment="center",
    )

    axs[row, (i * 2)].tick_params(axis="both", which="major", labelsize=12)

    ########################
    # the second axes
    ########################

    axs[row, (i * 2) + 1].set_xlabel("mm/yr/m", fontsize=12)
    axs[row, (i * 2) + 1].xaxis.set_label_position("top")
    axs[row, (i * 2) + 1].xaxis.label.set_color("red")

    axs[row, (i * 2) + 1].vlines(
        strain["Strain"] * 1000,
        strain["upper bounds"] / 100,
        strain["lower bounds"] / 100,
        color="red",
    )

    axs[row, (i * 2) + 1].spines["right"].set_visible(False)
    axs[row, (i * 2) + 1].spines["bottom"].set_visible(False)
    axs[row, (i * 2) + 1].spines["left"].set_zorder(1)

    axs[row, (i * 2) + 1].set_xlim([-15, 0.75])
    axs[row, (i * 2) + 1].set_xticks([-15, -7.5, 0])

    axs[row, (i * 2) + 1].spines["left"].set_position("zero")

    axs[row, (i * 2) + 1].tick_params(axis="both", which="major", labelsize=12)

    ########################
    # the parasite axis
    ########################
    par = axs[row, (2 * i) + 1].twiny()
    par.spines["top"].set_position(("axes", 1.2))

    make_patch_spines_invisible(par)
    par.spines["top"].set_visible(True)
    par.xaxis.set_label_position("top")
    par.xaxis.set_ticks_position("top")

    par.set_xlabel("c (%)", fontsize=12)
    par.set_xlim([-5, 100])
    par.vlines(
        strain["Contribution to subsidence (%).1"],
        strain["upper bounds"] / 100,
        strain["lower bounds"] / 100,
        color="dodgerblue",
        zorder=3,
    )
    par.xaxis.label.set_color("dodgerblue")
    par.tick_params(axis="x", labelcolor="dodgerblue")
    par.tick_params(axis="both", which="major", labelsize=12)

    axs[row, (i * 2) + 1].tick_params(axis="x", labelcolor="red")
    axs[row, (i * 2) + 1].tick_params(
        top=True, labeltop=True, bottom=False, labelbottom=False
    )

    ########################
    # plot a legend in the bottom right corner
    ########################

    if (row == 1) & (i == 1):

        handles = []

        for soiltype, color in SOILTYPES_COLORS.items():
            if soiltype in soiltypes_at_nobv_locations_for_legend:
                handles.append(mpatches.Patch(color=color, label=soiltype))

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

        soilprofile_legend = axs[row, (i * 2)].legend(
            handles=handles,
            bbox_to_anchor=(4.5, 1),
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

    axs[row, (i * 2)].invert_yaxis()
    axs[row, (i * 2) + 1].invert_xaxis()


axs[0, 0].set_ylabel("m below surface level", fontsize=12)
axs[1, 0].set_ylabel("m below surface level", fontsize=12)

axs[1, -1].set_visible(False)
axs[1, -2].set_visible(False)


fig.subplots_adjust(hspace=0.48)

outputdir = Path(
    r"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging"
)

plt.savefig(
    outputdir.joinpath(
        "data",
        "5-visualisation",
        "soilprofiles_contribution_strain_nobv_locations.png",
    ),
    bbox_inches="tight",
    dpi=300,
)
