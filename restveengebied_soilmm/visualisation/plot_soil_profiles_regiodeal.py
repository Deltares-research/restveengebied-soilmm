from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

from nobv_soilmm.read import read_soilprofile, read_strain, read_soilprofile_regiodeal
from nobv_soilmm.constants import (
    LOCATION_FULLNAMES,
    SOILPROFILE_DEPTHS,
    SOILTYPES_COLORS_DUTCH,
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

linestyle_tuple = [
    ("loosely dotted", (0, (1, 10))),
    ("dotted", (0, (1, 5))),
    ("densely dotted", (0, (1, 1))),
    ("long dash with offset", (5, (10, 3))),
    ("loosely dashed", (0, (5, 10))),
    ("dashed", (0, (5, 5))),
    ("densely dashed", (0, (5, 1))),
    ("loosely dashdotted", (0, (3, 10, 1, 10))),
    ("dashdotted", (0, (3, 5, 1, 5))),
    ("densely dashdotted", (0, (3, 1, 1, 1))),
    ("dashdotdotted", (0, (3, 5, 1, 5, 1, 5))),
    ("loosely dashdotdotted", (0, (3, 10, 1, 10, 1, 10))),
    ("densely dashdotdotted", (0, (3, 1, 1, 1, 1, 1))),
]

# locations = ["ZEG", "ROU", "ALB", "VLI", "ASD"]
locations = ["GDA", "HZW", "BKG", "BKW", "CBW"]

width_soil = 2
width_strain = 3

# soiltypes_at_nobv_locations_for_legend = [
#     "clay",
#     "peat",
#     "peat, clayey",
#     "sand",
#     "sand, mixed \nwith clay and/or silt",
#     "sand/loam",
#     "loam/sand",
# ]
soiltypes_at_regiodeal_locations_for_legend = [
    "klei",
    "klei, humeus",
    "veen",
    "veen, kleiig",
    "zand",
    "zand, humeus",
]

# see this link for adding a parasite axis: https://stackoverflow.com/questions/20146652/two-y-axis-on-the-left-side-of-the-figure


fig, axs = plt.subplots(
    nrows=2,
    ncols=8,
    sharey=True,
    gridspec_kw={
        "width_ratios": [width_soil, width_strain] * 3 + [width_strain, width_strain]
    },  # 3 is the amount of locations on one row
    figsize=(6.4 * 4 / 1.5, 9.6),
    squeeze=False,
)

for i, location in enumerate(locations):

    location_fullname = LOCATION_FULLNAMES[location]
    print(f"Plotting data for location: {location_fullname}")

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
    ]:
        soilprofile_lithology, soilprofile_anchors = read_soilprofile(
            location, location_fullname, language="dutch"
        )
    elif location in ["GDA"]:
        soilprofile_lithology, soilprofile_anchors = read_soilprofile_regiodeal(
            location, location_fullname
        )

    if location in ["ZEG", "ROU", "ALB", "VLI", "ASD"]:
        path_stats = r"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging/data/4-output/trendlijn_statistieken.xlsx"
    elif location in ["GDA", "HZW", "BKG", "BKW", "CBW"]:
        path_stats = r"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging/data/4-output/trendlijn_statistieken_regiodeal.xlsx"

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
            color=SOILTYPES_COLORS_DUTCH[lith[0]],
            zorder=1,
        )

    axs[row, (i * 2)].set_xlim([-0.4, 0.4])
    axs[row, (i * 2)].set_ylim(0, SOILPROFILE_DEPTHS["BKG"])

    axs[row, (i * 2)].get_xaxis().set_ticks(
        []
    )  # this turns off the text at the top of the bar

    if location == "HZW":
        plot_title = location_fullname.removesuffix("-Dorp")
    else:
        plot_title = location_fullname

    if row == 0:
        axs[row, (i * 2)].text(
            x=1.05,
            y=1.55,
            s=plot_title,
            fontsize=14,
            transform=axs[row, (i * 2)].transAxes,
            horizontalalignment="center",
        )
    else:
        axs[row, (i * 2)].text(
            x=1.05,
            y=1.35,
            s=plot_title,
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

    if location in ["BKG"]:
        nr_of_loops = 2
        headers = [3, 13]
        footers = [7, 0]
        linestyles = ["-", "-"]  # ["-", (0, (1, 0.5))]
        alphas = [1, 1]
        # alphas = [0.5, 0.5]
    else:
        nr_of_loops = 1
        headers = [2]
        footers = [0]
        linestyles = ["-"]
        alphas = [1]

    # for i in range(nr_of_loops):
    #     strain = read_strain(
    #         path_stats,
    #         sheetname=location_fullname,
    #         header=headers[i],
    #         footer=footers[i],
    #     )

    #     axs[row, (i * 2) + 1].vlines(
    #         strain["Strain"] * 1000,
    #         strain["upper bounds"] / 100,
    #         strain["lower bounds"] / 100,
    #         color="red",
    #     )

    axs[row, (i * 2) + 1].spines["right"].set_visible(False)
    axs[row, (i * 2) + 1].spines["bottom"].set_visible(False)
    axs[row, (i * 2) + 1].spines["left"].set_zorder(1)

    axs[row, (i * 2) + 1].set_xlim([-25, 8])
    axs[row, (i * 2) + 1].set_xticks([-20, -10, 0])

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
    par.set_xlim([-45, 150])
    par.set_xticks([0, 50, 100])

    for k in range(nr_of_loops):
        strain = read_strain(
            path_stats,
            sheetname=location_fullname,
            header=headers[k],
            footer=footers[k],
        )

        axs[row, (i * 2) + 1 + k].vlines(
            strain["Strain"] * 1000,
            strain["upper bounds"] / 100,
            strain["lower bounds"] / 100,
            color="red",
            linestyle=linestyles[k],
            alpha=alphas[k],
        )

        if k == 1:

            par2 = axs[row, (2 * i) + 2].twiny()
            par2.spines["top"].set_position(("axes", 1.2))

            make_patch_spines_invisible(par2)
            par2.spines["top"].set_visible(True)
            par2.xaxis.set_label_position("top")
            par2.xaxis.set_ticks_position("top")

            par2.set_xlabel("c (%)", fontsize=12)
            par2.set_xlim([-45, 150])
            par2.set_xticks([0, 50, 100])

            par2.vlines(
                strain["Contribution to subsidence (%).1"],
                strain["upper bounds"] / 100,
                strain["lower bounds"] / 100,
                color="dodgerblue",
                zorder=3,
                linestyle=linestyles[k],
                alpha=alphas[k],
            )

            par2.xaxis.label.set_color("dodgerblue")
            par2.tick_params(axis="x", labelcolor="dodgerblue")
            par2.tick_params(axis="both", which="major", labelsize=12)

            # axs[row, (i * 2) + 2].xaxis.tick_top() # this command does not seem to do anything yet

            axs[row, (i * 2) + 2].set_xlabel("mm/yr/m", fontsize=12)
            axs[row, (i * 2) + 2].xaxis.set_label_position("top")
            axs[row, (i * 2) + 2].xaxis.set_ticks_position("top")
            axs[row, (i * 2) + 2].xaxis.label.set_color("red")

            axs[row, (i * 2) + 2].spines["right"].set_visible(False)
            axs[row, (i * 2) + 2].spines["bottom"].set_visible(False)
            axs[row, (i * 2) + 2].spines["left"].set_zorder(1)

            axs[row, (i * 2) + 2].set_xlim([-25, 8])
            axs[row, (i * 2) + 2].set_xticks([-20, -10, 0])

            axs[row, (i * 2) + 2].spines["left"].set_position("zero")

            axs[row, (i * 2) + 2].tick_params(axis="both", which="major", labelsize=12)
            axs[row, (i * 2) + 2].tick_params(axis="x", labelcolor="red")

            axs[row, (i * 2) + 2].invert_xaxis()

        else:
            par.vlines(
                strain["Contribution to subsidence (%).1"],
                strain["upper bounds"] / 100,
                strain["lower bounds"] / 100,
                color="dodgerblue",
                zorder=3,
                linestyle=linestyles[k],
                alpha=alphas[k],
            )

    if location == "BKG":
        # import matplotlib.lines as mlines

        # black_line = mlines.Line2D(
        #     [],
        #     [],
        #     color="black",
        #     marker="s",
        #     linestyle="-",
        #     alpha=0.5,
        #     markersize=0,
        #     label="Periode tot\n14-09-2023",
        # )
        # black_line2 = mlines.Line2D(
        #     [],
        #     [],
        #     color="black",
        #     marker="s",
        #     linestyle=(0, (1, 0.5)),
        #     alpha=0.5,
        #     markersize=0,
        #     label="Periode vanaf\n05-11-2023",
        # )

        # soilprofile_legend = axs[row, (i * 2) + 1].legend(
        #     handles=[black_line, black_line2],
        #     bbox_to_anchor=(0.8, 0.6),
        #     loc="upper center",
        #     frameon=False,
        #     fontsize=10,
        #     ncol=1,
        #     # title="Bodemtypes:",
        #     # title_fontsize=14,
        #     alignment="left",
        # )

        axs[row, (i * 2) + 1].text(
            x=0.5,
            y=1.4,
            s="Periode tot\n14-09-2023",
            fontsize=14,
            transform=axs[row, (i * 2) + 1].transAxes,
            horizontalalignment="center",
        )

        axs[row, (i * 2) + 2].text(
            x=0.5,
            y=1.4,
            s="Periode vanaf\n05-11-2023",
            fontsize=14,
            transform=axs[row, (i * 2) + 2].transAxes,
            horizontalalignment="center",
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

        for soiltype, color in SOILTYPES_COLORS_DUTCH.items():
            if soiltype in soiltypes_at_regiodeal_locations_for_legend:
                handles.append(mpatches.Patch(color=color, label=soiltype))

        # this to add a triangle symbol for the anchors to the legend
        point = Line2D(
            [0],
            [0],
            label="anker",
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
            title="Bodemtypes:",
            title_fontsize=14,
            alignment="left",
        )

        # this sets the whitespace between the legend title and the legend entries
        soilprofile_legend._legend_box.sep = 12

    # axs[row, (i * 2) + 1].set_zorder(-1)

    axs[row, (i * 2)].invert_yaxis()
    axs[row, (i * 2) + 1].invert_xaxis()


axs[0, 0].set_ylabel("m onder maaiveld", fontsize=12)
axs[1, 0].set_ylabel("m onder maaiveld", fontsize=12)

axs[1, -1].set_visible(False)
axs[1, -2].set_visible(False)
axs[1, -3].set_visible(False)
axs[1, -4].set_visible(False)
axs[0, -1].set_visible(False)

fig.subplots_adjust(hspace=0.48)

outputdir = Path(
    r"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging"
)

plt.savefig(
    outputdir.joinpath(
        "data",
        "5-visualisation",
        "soilprofiles_contribution_strain_regiodeal_locations.png",
    ),
    bbox_inches="tight",
    dpi=300,
)
