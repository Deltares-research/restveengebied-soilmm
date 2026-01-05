import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA

from matplotlib import gridspec

from restveengebied_soilmm.read import read_soilprofile, read_strain
from restveengebied_soilmm.constants import (
    LOCATION_FULLNAMES,
    SOILPROFILE_DEPTHS,
    SOILTYPES_COLORS,
)

# mpl.rcParams["xtick.top"] = True
# mpl.rcParams["xtick.labeltop"] = True
# mpl.rcParams["xtick.bottom"] = False
# mpl.rcParams["xtick.labelbottom"] = False

locations = ["ZEG", "ROU"]
plot_type = "RF"

width_soil = 2
width_strain = 3

gs = gridspec.GridSpec(
    1, len(locations) * 2, width_ratios=[width_soil, width_strain] * len(locations)
)

# see this link tomorrow: https://stackoverflow.com/questions/20146652/two-y-axis-on-the-left-side-of-the-figure


# fig, axs = plt.subplots(
#     nrows=1,
#     ncols=len(locations) * 2,
#     sharey=True,
#     gridspec_kw={"width_ratios": [width_soil, width_strain] * len(locations)},
# )

# if not isinstance(axs, np.ndarray):
#     axs = np.array([axs])

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

    host = host_subplot(gs[i * 2], axes_class=AA.Axes)

    if i == 0:
        ax0 = host
    elif i > 0:
        host.set_yticklabels([])

    # plot the anchor depths
    for anchor in soilprofile_anchors["m-mv"]:
        host.hlines(anchor * 100 * -1, -1, 1, color="black", zorder=2)

        host.plot(
            0.44, anchor * 100 * -1, "<", color="black", markersize=5, clip_on=False
        )

    # plot the bars
    for lith in soilprofile_lithology.iterrows():
        host.bar(
            "Soil \n composition",
            lith[1]["dikte"],
            bottom=lith[1]["bovengrens [cm]"],
            label=lith[0],
            color=SOILTYPES_COLORS[lith[0]],
            zorder=1,
        )

    host.set_xlim([-0.4, 0.4])
    host.set_ylim(0, SOILPROFILE_DEPTHS["ASD"] * 100)

    # host.invert_yaxis()

    # host.xaxis.tick_top()
    host.get_xaxis().set_ticks([])  # this turns off the text at the top of the bar

    host.text(
        x=1.05,
        y=1.1,
        s=location_fullname,
        fontsize=14,
        transform=host.transAxes,
        horizontalalignment="center",
    )

    # host.tick_params(
    #     axis="both",
    #     which="both",
    #     # labelbottom=False,
    #     # labelleft=False,
    #     bottom=False,
    #     top=False,
    #     right=False,
    #     # labeltop=False,
    # )

    host2 = host_subplot(gs[(i * 2) + 1], axes_class=AA.Axes)
    #     # host2.invert_yaxis()
    #     # host2.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)

    par1 = host2.twiny()
    new_fixed_axis = par1.get_grid_helper().new_fixed_axis
    par1.axis["top"] = par1.new_fixed_axis(loc="top", offset=(0, 60))
    par1.axis["top"].label.set_color("red")
    par1.axis["top"].toggle(all=True)

    host.set_zorder(1)
    par1.set_zorder(2)

#     par1.vlines(
#         strain["Strain"] * 1000,
#         strain["upper bounds"],
#         strain["lower bounds"],
#         color="red",
#     )

#     # host2.axis["top"].label = "test"
#     # host2.axis["top"].label.set_color("dodgerblue")

#     # par1.invert_yaxis()
#     # host2.invert_yaxis()

#     host2.set_ylim(0, SOILPROFILE_DEPTHS["ASD"] * 100)
#     # host2.invert_yaxis()

#     host2.set_yticklabels([])
#     # host2.xaxis.set_label_text('mm/yr/m')
#     # host2.axes.set_xlabel("test")

#     # host2.set_xlabel("c (%)")
#     par1.set_xlabel("mm/yr/m")

#     par1.invert_xaxis()

#     # axs[(i * 2) + 1].stairs(y, edges=x, orientation='horizontal')
#     host2.vlines(
#         strain["Contribution to subsidence (%).1"],
#         strain["upper bounds"],
#         strain["lower bounds"],
#         color="dodgerblue",
#     )

#     # host2.spines["right"].set_visible(False)
#     # host2.spines["bottom"].set_visible(False)
#     # host2.axis["right"].set_visible(False)
#     # host2.axis["bottom"].set_visible(False)

#     # host.axis["left"].major_ticks = [""]

#     # host2.tick_params(
#     #     axis="both",
#     #     which="both",
#     #     labelbottom=False,
#     #     labelleft=False,
#     #     bottom=False,
#     #     right=False,
#     #     left=False,
#     # )

#     # host2.yaxis.tick_left()

#     # host2.set_xlabel("strain")

#     host2.set_xlim([-5, 100])
#     host2.axvline(color="black", linewidth=0.5, linestyle="--")

#     # host2.xaxis.set_tick_params(
#     #     "both",
#     #     {
#     #         "bottom": False,
#     #         "top": True,
#     #         "labelbottom": False,
#     #         "labeltop": True,
#     #     },
#     # )

#     # host2.get_yaxis().set_ticks([])  # this turns off the text at the top of the bar
#     host.invert_yaxis()
#     host2.invert_yaxis()

# ax0.set_ylabel("cm below surface level")

plt.show()
