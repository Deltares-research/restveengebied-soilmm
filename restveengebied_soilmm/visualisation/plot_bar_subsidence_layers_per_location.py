import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

from restveengebied_soilmm.constants import LOCATION_FULLNAMES

locations = ["HZW"]

relative_contributions = pd.DataFrame()

for location in locations:
    location_fullname = LOCATION_FULLNAMES[location]

    print(f"Analysing {location_fullname}")

    if location_fullname == "Bleskensgraaf":

        nr_of_loops = 2
        header = [3, 13]
        skipfooter = [11, 1]
        column_names = [
            f"{location_fullname}\ntot 14 september 2023",
            f"{location_fullname}\nvanaf 5 november 2023",
        ]

    else:
        nr_of_loops = 1
        header = [2]
        skipfooter = [1]
        column_names = [location_fullname]

    for i in range(nr_of_loops):
        relative_contribution = pd.read_excel(
            r"n:\Projects\11211000\11211391\B. Measurements and calculations\Bodembeweging\data\4-output\trendlijn_statistieken_regiodeal.xlsx",
            sheet_name=location_fullname,
            header=header[i],
            usecols="I",
            skipfooter=skipfooter[i],
        )
        relative_contribution.columns = [column_names[i]]

        # count from 1
        relative_contribution.index += 1

        relative_contribution = relative_contribution.T

        if relative_contributions.empty:
            relative_contributions = relative_contribution
        else:
            relative_contributions = pd.concat(
                [relative_contributions, relative_contribution], axis=0
            )

    colors = plt.cm.viridis_r(np.linspace(0, 1, len(relative_contributions.columns)))

    fig, ax = plt.subplots(figsize=(10, 3.5))

    relative_contributions.plot.barh(ax=ax, stacked=True, rot=0, color=colors).legend(
        title="Laag:",
        loc="upper center",
        bbox_to_anchor=(0.5, -0.225),
        fancybox=True,
        ncol=5,
    )
    ax.axvline(x=0, linestyle="-", color="black", linewidth=0.5)
    # ax.legend().set_loc("lower right")
    # ax.legend().set_title("Anker:")

    ax.set_xlabel("Bijdrage aan bodemdaling (%)")

    outputdir = Path(
        r"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging"
    )

    # ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
    #   fancybox=True, shadow=True, ncol=5)

    plt.savefig(
        outputdir.joinpath(
            "data",
            "5-visualisation",
            location_fullname,
            "Layer_contribution_to_subsidence.png",
        ),
        bbox_inches="tight",
        dpi=300,
    )

# plt.show()
