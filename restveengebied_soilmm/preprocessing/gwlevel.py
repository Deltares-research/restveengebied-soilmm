from pathlib import Path
import pandas as pd
import numpy as np

from nobv_soilmm.constants import LOCATION_FULLNAMES


def load_column_letters(location_fullname, column="B"):
    match location_fullname:
        case (
            "Gouda_MBORijnland"
            | "Berkenwoude"
            | "Bleskensgraaf"
            | "Cabauw"
            | "Hazerswoude-Dorp"
            | "Moordrecht-Middelweg"
            | "Moordrecht-4eTochtweg"
            | "Moordrecht-Spoorweglaan"
        ):
            anchor_columns = list(column)

    return anchor_columns


def read_gwlevel(location, location_fullname, period="h"):
    """
    Read groundwater level data from an Excel file and resample it to the specified period.

    Parameters:
    - location: Short code for the location (e.g., "GOU").
    - location_fullname: Full name of the location (e.g., "Gouda_MBORijnland").
    - period: Resampling period (default is "h" for hourly).

    Returns:
    - DataFrame with resampled groundwater level data.
    """

    if location == "HZW":
        filename = location_fullname.removesuffix("-Dorp")
    else:
        filename = location_fullname

    match location:
        case "GDA" | "BKW" | "BKG" | "CBW" | "HZW":
            basedir = Path(
                r"n:/Projects/11206000/11206020/B. Measurements and calculations"
            )
        case "M4T" | "MMW" | "MSW":
            basedir = Path(
                r"n:/Projects/11210000/11210175/B. Measurements and calculations"
            )

    path_to_data = basedir.joinpath("Extensometers", f"{filename}.xlsm")

    outputdir = Path(
        r"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging/data/2-interim"
    )

    anchor_columns = load_column_letters(location_fullname, column="B")

    match location_fullname:
        case (
            "Gouda_MBORijnland"
            | "Berkenwoude"
            | "Bleskensgraaf"
            | "Cabauw"
            | "Hazerswoude-Dorp"
            | "Moordrecht-Middelweg"
            | "Moordrecht-4eTochtweg"
            | "Moordrecht-Spoorweglaan"
        ):
            sheetname = "PB"

    ## load raw data from excel
    data = (
        pd.read_excel(
            path_to_data,
            sheet_name=sheetname,
            skiprows=[0, 1, 2, 3, 4, 6, 7, 8],
            usecols=[0] + [ord(letter) - 65 for letter in anchor_columns],
            index_col=0,
        )
        .resample(period)
        .mean()
    ) * 100

    data.columns = ["Waterstand"]

    data.to_csv(outputdir.joinpath(location_fullname, f"{location}_gwlevel.csv"))

    return data


def read_gwlevel_rou09(filename_wareco, period="h", plot_type="RF"):
    """
    Read groundwater level data from an Excel file and resample it to the specified period.

    Parameters:
    - location: Short code for the location (e.g., "ROU09").
    - location_fullname: Full name of the location (e.g., "Rouveen_parcel09").
    - period: Resampling period (default is "h" for hourly).

    Returns:
    - DataFrame with resampled groundwater level data.
    """

    farmer = "09"
    name = f"GW-{farmer}"
    # print(f'Loading groundwater data for {name}_{plot}.')

    # for name in names:
    if plot_type == "RF":  # referentie perceel
        excel_cols = "A:B"
    elif plot_type == "MS":  # maatregelen perceel
        excel_cols = "E:F"

    rows_to_skip = 5

    gwstand_wareco = (
        pd.read_excel(
            filename_wareco,
            sheet_name=name,
            index_col=0,
            skiprows=rows_to_skip,
            usecols=excel_cols,
        )
        # .resample(period)
        # .mean()
        # .squeeze()
    )

    gwstand_wareco *= 100  # to convert from m to cm

    gwstand_wareco.columns = ["Waterstand (m NAP)"]
    gwstand_wareco.index.names = ["Datum"]

    gwstand_wareco /= 100

    gwstand_wareco = gwstand_wareco.dropna()

    gwstand_wareco.columns = ["Waterstand"]

    # gwstand_wareco[f'{name}_RF'] /= 100
    # gwstand[f'{name}_MP'] /= 100

    # return data
    # return gwstand_wareco, gwstand_nobv
    return gwstand_wareco


def read_hydraulic_head(location, location_fullname, period="h"):
    """
    Read groundwater level data from an Excel file and resample it to the specified period.

    Parameters:
    - location: Short code for the location (e.g., "GOU").
    - location_fullname: Full name of the location (e.g., "Gouda_MBORijnland").
    - period: Resampling period (default is "h" for hourly).

    Returns:
    - DataFrame with resampled groundwater level data.
    """

    if location == "HZW":
        filename = location_fullname.removesuffix("-Dorp")
    else:
        filename = location_fullname

    match location:
        case "GDA" | "BKW" | "BKG" | "CBW" | "HZW":
            basedir = Path(
                r"n:/Projects/11206000/11206020/B. Measurements and calculations"
            )
            column = "C"
        case "MMW" | "M4T" | "MSW":
            basedir = Path(
                r"n:/Projects/11210000/11210175/B. Measurements and calculations"
            )
            if location in ["MMW", "MSW"]:
                column = "E"
            elif location == "M4T":
                column = "D"

    path_to_data = basedir.joinpath("Extensometers", f"{filename}.xlsm")

    anchor_columns = load_column_letters(location_fullname, column=column)

    match location_fullname:
        case (
            "Gouda_MBORijnland"
            | "Berkenwoude"
            | "Bleskensgraaf"
            | "Cabauw"
            | "Hazerswoude-Dorp"
            | "Moordrecht-Middelweg"
            | "Moordrecht-4eTochtweg"
            | "Moordrecht-Spoorweglaan"
        ):
            sheetname = "PB"

    ## load raw data from excel
    data = (
        pd.read_excel(
            path_to_data,
            sheet_name=sheetname,
            skiprows=[0, 1, 2, 3, 4, 6, 7, 8],
            usecols=[0] + [ord(letter) - 65 for letter in anchor_columns],
            index_col=0,
        )
        .resample(period)
        .mean()
    ) * 100

    data.columns = ["Waterstand"]

    outputdir = Path(
        r"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging/data/2-interim"
    )

    data.to_csv(outputdir.joinpath(location_fullname, f"{location}_hydraulic_head.csv"))

    return data


def read_ditch_level(location, location_fullname, period="h"):
    """
    Read groundwater level data from an Excel file and resample it to the specified period.

    Parameters:
    - location: Short code for the location (e.g., "GOU").
    - location_fullname: Full name of the location (e.g., "Gouda_MBORijnland").
    - period: Resampling period (default is "h" for hourly).

    Returns:
    - DataFrame with resampled groundwater level data.
    """

    if location == "HZW":
        filename = location_fullname.removesuffix("-Dorp")
    else:
        filename = location_fullname

    match location:
        case "GDA" | "BKW" | "BKG" | "HZW":
            basedir = Path(
                r"n:/Projects/11206000/11206020/B. Measurements and calculations"
            )
            column = "J"
            index_col = "F"
            skiprows = [0, 1, 2, 3, 4, 6]

        case "CBW":
            basedir = Path(
                r"n:/Projects/11206000/11206020/B. Measurements and calculations"
            )
            column = "N"
            index_col = "J"
            skiprows = [0, 1, 2, 3, 4, 6, 7]
        case "MMW" | "M4T" | "MSW":
            basedir = Path(
                r"n:/Projects/11210000/11210175/B. Measurements and calculations"
            )
            if location == "MMW":
                column = "L"
                index_col = "H"
                skiprows = [0, 1, 2, 3, 4, 6, 7]
            elif location == "MSW":
                column = "M"
                index_col = "I"
                skiprows = [0, 1, 2, 3, 4, 6, 7, 8]
            elif location == "M4T":
                column = "K"
                index_col = "G"
                skiprows = [0, 1, 2, 3, 4]

    path_to_data = basedir.joinpath("Extensometers", f"{filename}.xlsm")

    anchor_columns = load_column_letters(location_fullname, column=column)
    index_column = load_column_letters(location_fullname, column=index_col)

    match location_fullname:
        case (
            "Gouda_MBORijnland"
            | "Berkenwoude"
            | "Bleskensgraaf"
            | "Cabauw"
            | "Hazerswoude-Dorp"
            | "Moordrecht-Middelweg"
            | "Moordrecht-4eTochtweg"
            | "Moordrecht-Spoorweglaan"
        ):
            sheetname = "PB"

    ## load raw data from excel
    data = pd.read_excel(
        path_to_data,
        sheet_name=sheetname,
        skiprows=skiprows,
        header=1,
        usecols=[ord(letter) - 65 for letter in index_column]
        + [ord(letter) - 65 for letter in anchor_columns],
        # index_col=[ord(letter) - 65 for letter in index_column],
        # usecols=[5, 9],
        # index_col=[5]
    )
    # .resample(period)
    # .mean()
    # ) * 100

    data = data.dropna()

    data.columns = ["tijd", "Waterstand"]

    data = data.set_index("tijd")

    data *= 100

    # mask data
    match location:
        case "BKW":
            data.loc["2025-04-23 11:00"] = np.nan
        case "M4T":
            data.loc[:"2024-10-23 13:00"] = np.nan

    outputdir = Path(
        r"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging/data/2-interim"
    )

    data.to_csv(outputdir.joinpath(location_fullname, f"{location}_ditch_level.csv"))

    return data


def read_pb(location, location_fullname, period="h", columns=["B"]):
    """
    Read groundwater level data from an Excel file and resample it to the specified period.

    Parameters:
    - location: Short code for the location (e.g., "GOU").
    - location_fullname: Full name of the location (e.g., "Gouda_MBORijnland").
    - period: Resampling period (default is "h" for hourly).

    Returns:
    - DataFrame with resampled groundwater level data.
    """

    if location == "HZW":
        filename = location_fullname.removesuffix("-Dorp")
    else:
        filename = location_fullname

    match location:
        case "GDA" | "BKW" | "BKG" | "CBW" | "HZW":
            basedir = Path(
                r"n:/Projects/11206000/11206020/B. Measurements and calculations"
            )
        case "M4T" | "MMW" | "MSW":
            basedir = Path(
                r"n:/Projects/11210000/11210175/B. Measurements and calculations"
            )

    path_to_data = basedir.joinpath("Extensometers", f"{filename}.xlsm")

    outputdir = Path(
        r"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging/data/2-interim"
    )

    # anchor_columns = load_column_letters(location_fullname, column=column)

    match location_fullname:
        case (
            "Gouda_MBORijnland"
            | "Berkenwoude"
            | "Bleskensgraaf"
            | "Cabauw"
            | "Hazerswoude-Dorp"
            | "Moordrecht-Middelweg"
            | "Moordrecht-4eTochtweg"
            | "Moordrecht-Spoorweglaan"
        ):
            sheetname = "PB"

    ## load raw data from excel
    data = (
        pd.read_excel(
            path_to_data,
            sheet_name=sheetname,
            skiprows=[0, 1, 2, 3, 4, 6, 7, 8],
            usecols=[0] + [ord(letter) - 65 for letter in columns],
            index_col=0,
        )
        .resample(period)
        .mean()
    ) * 100

    data.columns = [f"Waterstand PB{nr+1}" for nr in range(len(columns))]

    data.to_csv(outputdir.joinpath(location_fullname, f"{location}_gwlevels.csv"))

    return data


# def read_middepth_filter(location, location_fullname, period="h"):
#     """
#     Read groundwater level data from an Excel file and resample it to the specified period.

#     Parameters:
#     - location: Short code for the location (e.g., "GOU").
#     - location_fullname: Full name of the location (e.g., "Gouda_MBORijnland").
#     - period: Resampling period (default is "h" for hourly).

#     Returns:
#     - DataFrame with resampled groundwater level data.
#     """

#     if location == "HZW":
#         filename = location_fullname.removesuffix("-Dorp")
#     else:
#         filename = location_fullname

#     match location:
#         case "GDA" | "BKW" | "BKG" | "CBW" | "HZW":
#             basedir = Path(
#                 r"n:/Projects/11206000/11206020/B. Measurements and calculations"
#             )
#             column = "C"
#         case "MMW" | "M4T":
#             basedir = Path(
#                 r"n:/Projects/11210000/11210175/B. Measurements and calculations"
#             )
#             if location == "MMW":
#                 column = "E"
#             elif location == "M4T":
#                 column = "C"

#     path_to_data = basedir.joinpath("Extensometers", f"{filename}.xlsm")

#     anchor_columns = load_column_letters(location_fullname, column=column)

#     match location_fullname:
#         case (
#             "Gouda_MBORijnland"
#             | "Berkenwoude"
#             | "Bleskensgraaf"
#             | "Cabauw"
#             | "Hazerswoude-Dorp"
#             | "Moordrecht-Middelweg"
#             | "Moordrecht-4eTochtweg"
#         ):
#             sheetname = "PB"

#     ## load raw data from excel
#     data = (
#         pd.read_excel(
#             path_to_data,
#             sheet_name=sheetname,
#             skiprows=[0, 1, 2, 3, 4, 6, 7, 8],
#             usecols=[0] + [ord(letter) - 65 for letter in anchor_columns],
#             index_col=0,
#         )
#         .resample(period)
#         .mean()
#     ) * 100

#     data.columns = ["Waterstand"]

#     outputdir = Path(
#         r"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging/data/2-interim"
#     )

#     data.to_csv(
#         outputdir.joinpath(location_fullname, f"{location}_middepth_filter.csv")
#     )

#     return data


if __name__ == "__main__":
    # # Example usage
    # location = "MMW"
    # period = "h"

    # location_fullname = LOCATION_FULLNAMES[location]
    # print(f"Processing data for {location_fullname}")

    # # gwlevel_data = read_gwlevel(location, location_fullname, period)
    # hydraulic_head_data = read_hydraulic_head(location, location_fullname, period)

    # location = "BKG"
    # locations = ["BKG", "BKW", "CBW", "HZW", "GDA"]
    # locations = ["BKW"]
    locations = ["M4T", "MMW", "MSW"]
    columns = [["B", "C", "D"], ["B", "C", "D", "E"], ["B", "C", "D", "E"]]
    # locations = ["BKW"]
    # locations = ["ROU09"]  # For testing Rouveen parcels
    # plot_types = ["RF", "MS"]
    period = "h"
    # location_fullname = "Gouda_MBORijnland"

    outputdir = Path(
        r"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging/data/2-interim"
    )

    for i, location in enumerate(locations):

        location_fullname = LOCATION_FULLNAMES[location]

        print(f"Processing data for {location_fullname}")

        # if location in ["ROU09"]:
        #     dir_path = Path(
        #         r"N:\Projects\11202500\11202992\B. Measurements and calculations\Waterpassingen"
        #     )
        #     path_to_groundwater_data = dir_path.joinpath(
        #         "Waterpassing bodemdaling Rouveen 2018-2023.xlsx"
        #     )

        #     for plot_type in plot_types:
        #         print(
        #             f"Reading groundwater level data for {location_fullname} - {plot_type}"
        #         )
        #         # Special case for Rouveen parcel 09
        #         gwlevel_data = read_gwlevel_rou09(
        #             path_to_groundwater_data, period, plot_type
        #         )

        #         path_to_csv = outputdir.joinpath(
        #             location_fullname, f"{location}_gwlevel_{plot_type}.csv"
        #         )

        #         gwlevel_data.to_csv(path_to_csv)

        if location in ["BKW", "BKG", "CBW", "HZW", "GDA"]:
            # gwlevel_data = read_gwlevel(location, location_fullname, period)

            # hydraulic_head_data = read_hydraulic_head(
            #     location, location_fullname, period
            # )

            ditch_level_data = read_ditch_level(location, location_fullname, period)

        if location in ["MMW", "M4T", "MSW"]:
            # gwlevel_data = read_gwlevel(location, location_fullname, period)
            # hydraulic_head_data = read_hydraulic_head(
            #     location, location_fullname, period
            # )
            # ditch_level_data = read_ditch_level(location, location_fullname, period)
            pb_data = read_pb(location, location_fullname, columns=columns[i])

    # print(gwlevel_data.head())
