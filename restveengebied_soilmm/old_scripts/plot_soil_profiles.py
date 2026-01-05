from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import OrderedDict
import matplotlib as mpl

import matplotlib.patches as mpatches

# from mpl_toolkits.axes_grid1 import host_subplot
# import mpl_toolkits.axisartist as AA

# from matplotlib import gridspec

from restveengebied_soilmm.read import read_soilprofile, read_strain
from restveengebied_soilmm.constants import (
    LOCATION_FULLNAMES,
    SOILPROFILE_DEPTHS,
    SOILTYPES_COLORS,
)

mpl.rcParams["xtick.top"] = True
mpl.rcParams["xtick.labeltop"] = True
mpl.rcParams["xtick.bottom"] = False
mpl.rcParams["xtick.labelbottom"] = False
plt.rcParams["axes.axisbelow"] = True


def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)


locations = ["ZEG", "ROU", "ALB", "VLI", "ASD"]
plot_type = "RF"

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

# gs = gridspec.GridSpec(
#     1, len(locations) * 2, width_ratios=[width_soil, width_strain] * len(locations)
# )

# see this link tomorrow: https://stackoverflow.com/questions/20146652/two-y-axis-on-the-left-side-of-the-figure


fig, axs = plt.subplots(
    nrows=1,
    ncols=len(locations) * 2,
    sharey=True,
    gridspec_kw={"width_ratios": [width_soil, width_strain] * len(locations)},
    figsize=(6.4 * len(locations) / 1.5, 4.8),
)

if not isinstance(axs, np.ndarray):
    axs = np.array([axs])

for i, location in enumerate(locations):

    location_fullname = LOCATION_FULLNAMES[location]
    print(f"Plotting data for location: {location_fullname}")

    soilprofile_depth = SOILPROFILE_DEPTHS[location]
    soilprofile_lithology, soilprofile_anchors = read_soilprofile(
        location, location_fullname, plot_type=plot_type
    )

    path_stats = r"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging/data/4-output/trendlijn_statistieken.xlsx"

    strain = read_strain(path_stats, sheetname=location_fullname)
    # x = strain.index.tolist()
    # y = strain["Contribution to subsidence (%).1"].dropna().tolist()

    # host = host_subplot(gs[i * 2], axes_class=AA.Axes)

    # if i == 0:
    #     ax0 = host
    # elif i > 0:
    #     host.set_yticklabels([])

    # plot the anchor depths
    for anchor in soilprofile_anchors["m-mv"]:
        axs[(2 * i)].hlines(anchor * 100 * -1, -1, 1, color="black", zorder=2)

        axs[(2 * i)].plot(
            0.44, anchor * 100 * -1, "<", color="black", markersize=5, clip_on=False
        )

    # plot the bars
    for lith in soilprofile_lithology.iterrows():
        axs[(i * 2)].bar(
            "Soil \n composition",
            lith[1]["dikte"],
            bottom=lith[1]["bovengrens [cm]"],
            label=lith[0],
            color=SOILTYPES_COLORS[lith[0]],
            zorder=1,
        )

    axs[(i * 2)].set_xlim([-0.4, 0.4])
    axs[(i * 2)].set_ylim(0, SOILPROFILE_DEPTHS["ASD"] * 100)

    # host.invert_yaxis()

    # # host.xaxis.tick_top()
    axs[(i * 2)].get_xaxis().set_ticks(
        []
    )  # this turns off the text at the top of the bar

    axs[(i * 2)].text(
        x=1.05,
        y=1.3,
        s=location_fullname,
        fontsize=14,
        transform=axs[(i * 2)].transAxes,
        horizontalalignment="center",
    )

    # axs[(i * 2) + 1].tick_params(
    #     axis="both",
    #     which="both",
    #     labelbottom=False,
    #     # labelleft=False,
    #     bottom=False,
    #     top=True,
    #     # right=False,
    #     labeltop=True,
    # )

    # axs[(i * 2) + 1].set_xlabel("c (%)")
    axs[(i * 2) + 1].set_xlabel("mm/yr/m")
    axs[(i * 2) + 1].xaxis.set_label_position("top")

    # axs[(i * 2)+1].get_xaxis().set_ticks([0, 50 , 100])
    # axs[(i * 2) + 1].get_xaxis().set_ticks_position("top")

    # host2 = host_subplot(gs[(i * 2) + 1], axes_class=AA.Axes)
    #     # host2.invert_yaxis()
    #     # host2.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)

    # par1 = host2.twiny()
    # new_fixed_axis = par1.get_grid_helper().new_fixed_axis
    # par1.axis["top"] = par1.new_fixed_axis(loc="top", offset=(0, 60))
    # par1.axis["top"].label.set_color("red")
    # par1.axis["top"].toggle(all=True)

    # host.set_zorder(1)
    # par1.set_zorder(2)

    # host2.axis["top"].label = "test"
    axs[(2 * i) + 1].xaxis.label.set_color("red")

    # axs[(2 * i) + 1].tick_params(axis="x", colors="dodgerblue")

    # par1.invert_yaxis()
    # host2.invert_yaxis()

    # host2.set_ylim(0, SOILPROFILE_DEPTHS["ASD"] * 100)
    # host2.invert_yaxis()

    # host2.set_yticklabels([])
    # host2.xaxis.set_label_text('mm/yr/m')
    # host2.axes.set_xlabel("test")

    # host2.set_xlabel("c (%)")
    # par1.set_xlabel("mm/yr/m")

    # par1.invert_xaxis()

    # axs[(i * 2) + 1].stairs(y, edges=x, orientation='horizontal')

    # axs[(i * 2) + 1].set_axisbelow(True)

    axs[(i * 2) + 1].vlines(
        strain["Strain"] * 1000,
        strain["upper bounds"],
        strain["lower bounds"],
        color="red",
    )

    axs[(i * 2) + 1].spines["right"].set_visible(False)
    axs[(i * 2) + 1].spines["bottom"].set_visible(False)
    axs[(i * 2) + 1].spines["left"].set_zorder(1)

    axs[(i * 2) + 1].set_xlim([-15, 0.75])
    axs[(i * 2) + 1].set_xticks([-15, -7.5, 0])

    axs[(i * 2) + 1].spines["left"].set_position("zero")

    # axs[(i * 2) + 1].axvline(
    #     x=0,
    #     # ymin=0,
    #     # ymax=1.15,
    #     color="black",
    #     linewidth=0.5,
    #     linestyle="--",
    #     clip_on=False,
    #     zorder=1,
    # )

    # host2.axis["right"].set_visible(False)
    # host2.axis["bottom"].set_visible(False)

    # host.axis["left"].major_ticks = [""]

    # host2.tick_params(
    #     axis="both",
    #     which="both",
    #     labelbottom=False,
    #     labelleft=False,
    #     bottom=False,
    #     right=False,
    #     left=False,
    # )

    # host2.yaxis.tick_left()

    # host2.set_xlabel("strain")

    ########################
    # the parasite axis
    ########################
    par = axs[(2 * i) + 1].twiny()
    par.spines["top"].set_position(("axes", 1.15))

    make_patch_spines_invisible(par)
    par.spines["top"].set_visible(True)
    par.xaxis.set_label_position("top")
    par.xaxis.set_ticks_position("top")
    # p, = par.plot(variables[ix][0], variables[ix][1], colors[ix], label=ylabels[ix])

    par.set_xlabel("c (%)")
    par.set_xlim([-5, 100])
    # par.set_xticks([-15, -7.5, 0])
    par.vlines(
        strain["Contribution to subsidence (%).1"],
        strain["upper bounds"],
        strain["lower bounds"],
        color="dodgerblue",
        zorder=3,
    )
    par.xaxis.label.set_color("dodgerblue")
    par.tick_params(axis="x", colors="dodgerblue")
    # lines.append(p)

    # host2.xaxis.set_tick_params(
    #     "both",
    #     {
    #         "bottom": False,
    #         "top": True,
    #         "labelbottom": False,
    #         "labeltop": True,
    #     },
    # )

    # host2.get_yaxis().set_ticks([])  # this turns off the text at the top of the bar
    # host.invert_yaxis()
    # host2.invert_yaxis()

    axs[(i * 2) + 1].tick_params(axis="x", colors="red")
    axs[(i * 2) + 1].tick_params(
        top=True, labeltop=True, bottom=False, labelbottom=False
    )

    if i == 0:

        handles = []

        for soiltype, color in SOILTYPES_COLORS.items():
            # print(soiltype, "->", color)
            if soiltype in soiltypes_at_nobv_locations_for_legend:
                handles.append(mpatches.Patch(color=color, label=soiltype))

        soilprofile_legend = axs[(i * 2)].legend(
            handles=handles,
            bbox_to_anchor=(2.1, 0.47),
            loc="upper center",
            frameon=False,
            fontsize=9,
            ncol=1,
            title="Soil types:",
        )

    # handles, labels = axs[(i * 2)].get_legend_handles_labels()

    # by_label = OrderedDict(zip(labels, handles))

    # # key_order = ["sand", "organic sand", "clay", "organic clay", "peat"]
    # # for k in key_order:  # a loop to force the order you want
    # #     by_label.move_to_end(k)

    # soilprofile_legend = axs[(i * 2)].legend(
    #     by_label.values(),
    #     by_label.keys(),
    #     bbox_to_anchor=(2.1, 0.4),
    #     loc="upper center",
    #     frameon=False,
    #     fontsize=9,
    #     ncol=1,
    #     title="Soil types:",
    # )

    # soilprofile_legend.set_zorder(102)
    # soilprofile_legend.get_frame().set_facecolor('w')

    axs[(i * 2) + 1].set_zorder(-1)

    axs[(i * 2)].invert_yaxis()
    axs[(i * 2) + 1].invert_xaxis()


axs[0].set_ylabel("cm below surface level")

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

# plt.show()
