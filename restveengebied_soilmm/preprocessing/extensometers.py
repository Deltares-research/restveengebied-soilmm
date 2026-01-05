from pathlib import Path
import pandas as pd
import numpy as np

# import sys

# sys.path.append(
#     r"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging/src"
# )

from nobv_soilmm.constants import LOCATION_FULLNAMES


def letter_range(start, stop="{", step=1):
    """Yield a range of lowercase letters."""
    for ord_ in range(ord(start.upper()), ord(stop.upper()), step):
        yield chr(ord_)


def load_column_letters(location_fullname):
    match location_fullname:
        case "Vegelinsoord":
            # anchor_columns = list(letter_range("G", "J"))
            anchor_columns = list(letter_range("D", "G"))
        case "Rouveen":
            # anchor_columns = list(letter_range("I", "M"))
            anchor_columns = list(letter_range("E", "I"))
        case "Rouveen_parcel09":
            anchor_columns = list(letter_range("D", "G"))
        case _:
            # anchor_columns = list(letter_range("M", "S"))
            anchor_columns = list(letter_range("G", "M"))

    return anchor_columns


def update_extensometer_data_firstseries(
    location, location_fullname, plot_type="RF", period="h"
):

    match location:
        case "ROU":
            basedir = Path(
                r"n:/Projects/11202000/11202008/B. Measurements and calculations/Extensometers"
            )
            if plot_type == "MS":
                path_to_data = basedir.joinpath("WDOD-05A-drain.xlsm")
            else:
                path_to_data = basedir.joinpath("WDOD-05B-ref.xlsm")
        case "ROU09":
            basedir = Path(
                r"n:/Projects/11202000/11202008/B. Measurements and calculations/Extensometers"
            )
            if plot_type == "MS":
                path_to_data = basedir.joinpath("WDOD-09A-drain.xlsm")
            else:
                path_to_data = basedir.joinpath("WDOD-09B-ref.xlsm")
        case _:
            basedir = Path(
                r"n:/Projects/11204000/11204108/B. Measurements and calculations/Extensometers/"
            )
            path_to_data = basedir.joinpath(f"{location}_{plot_type}.xlsm")

    if location == "ZEG":
        if plot_type == "MS":
            path_to_data = basedir.joinpath(f"{location}_003_perceel 16-drain.xlsm")

    outputdir = Path(
        r"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging/data/2-interim"
    )

    anchor_columns = load_column_letters(location_fullname)

    ## load raw data from excel
    df = pd.read_excel(
        path_to_data,
        sheet_name="bewerking",
        header=4,
        # skiprows = [0,1,2,4],
        usecols=[0] + [ord(letter) - 65 for letter in anchor_columns],
    )

    names = df.iloc[0, 1:].values.tolist()

    ## rename columns
    new_names = []
    for name in names:
        name = name.replace(",", ".")
        new_names.append(name.replace("MV -", "") + "-mv")
    df.columns = df.columns[:1].tolist() + new_names
    df = df.iloc[4:]

    df.tijd = pd.to_datetime(df.tijd)

    ## set index to datetime
    df = df.set_index("tijd")  # .loc[~df.index.duplicated(keep="first")]
    df = df[~df.index.duplicated(keep="first")]

    # print(df)

    # df.index = pd.to_datetime(df.index)
    df = df.resample(period).mean()

    if (location == "ROU09") and (plot_type == "MS"):
        df.loc["2025-02-01":] = np.nan

    df.to_csv(
        outputdir.joinpath(
            location_fullname, f"{location}_extensometer_{plot_type}.csv"
        )
    )

    return df


def read_file(path_to_data, sheetname, location_fullname, usecols=None):
    """
    This is an example function made by Bas Knaake, which serves only one purpose,
    namely to read data from an excel file.
    """

    if usecols is None:
        usecols = [0] + [
            ord(letter) - 65 for letter in load_column_letters(location_fullname)
        ]
    anchor_columns = load_column_letters(location_fullname)
    df = pd.read_excel(
        path_to_data,
        sheet_name=sheetname,
        skiprows=[0, 1, 2, 3, 4, 6, 7, 8],
        usecols=[0] + [ord(letter) - 65 for letter in anchor_columns],
        index_col=0,
    )
    return df


def update_extensometer_data_secondseries(location, location_fullname, period="h"):

    basedir = Path(r"n:/Projects/11206000/11206457/B. Measurements and calculations")
    path_to_data = basedir.joinpath(
        location_fullname, "Extensometer", f"{location_fullname}.xlsm"
    )

    outputdir = Path(
        r"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging/data/2-interim"
    )

    anchor_columns = load_column_letters(location_fullname)

    match location_fullname:
        case "Demmerik" | "Vegelinsoord":
            sheetname = "Ext"
        case "LangeWeide":
            sheetname = "EXT"
        case "ZegveldHoogwater":
            sheetname = "bewerking"

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
    )

    new_column_names = []
    for name in data.columns.tolist():
        name = name.replace("MV -", "")
        new_column_names.append(name + "-mv")

    data.columns = new_column_names

    data.to_csv(outputdir.joinpath(location_fullname, f"{location}_extensometer.csv"))

    return data


def update_extensometer_data_regiodeal(location, location_fullname, period="h"):

    basedir = Path(r"n:/Projects/11206000/11206020/B. Measurements and calculations")

    if location == "HZW":
        filename = location_fullname.removesuffix("-Dorp")
    else:
        filename = location_fullname

    path_to_data = basedir.joinpath("Extensometers", f"{filename}.xlsm")

    outputdir = Path(
        r"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging/data/2-interim"
    )

    anchor_columns = load_column_letters(location_fullname)

    # match location_fullname:
    #     case "Gouda_MBORijnland" | "Berkenwoude":
    sheetname = "Ext"

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
    )

    new_column_names = []
    for name in data.columns.tolist():
        name = name.replace("MV -", "")
        new_column_names.append(name + "-mv")

    data.columns = new_column_names

    if location == "BKW":
        data.loc["2024-07-25 10:00"] = np.nan
    elif location == "HZW":
        data.loc["2023-05-24 14:00", "2.60 m-mv"] = np.nan

    data.to_csv(outputdir.joinpath(location_fullname, f"{location}_extensometer.csv"))

    return data


def update_extensometer_data_moordrecht(location, location_fullname, period="h"):

    basedir = Path(r"n:/Projects/11210000/11210175/B. Measurements and calculations")
    path_to_data = basedir.joinpath("Extensometers", f"{location_fullname}.xlsm")

    outputdir = Path(
        r"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging/data/2-interim"
    )

    anchor_columns = load_column_letters(location_fullname)

    # match location_fullname:
    #     case "Gouda_MBORijnland" | "Berkenwoude":
    sheetname = "Ext"

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
    )

    new_column_names = []
    for name in data.columns.tolist():
        name = name.replace("MV -", "")
        new_column_names.append(name + "-mv")

    data.columns = new_column_names

    data.to_csv(outputdir.joinpath(location_fullname, f"{location}_extensometer.csv"))

    return data


def update_extensometer_data(locations, period="h", plot_type="RF"):

    for location in locations:
        location_fullname = LOCATION_FULLNAMES[location]

        print(f"Processing data for {location_fullname}")

        match location:
            case "ALB" | "ASD" | "ROU" | "VLI" | "ZEG" | "ROU09":
                extensometer_data = update_extensometer_data_firstseries(
                    location, location_fullname, period=period, plot_type=plot_type
                )
            case "DEM" | "LW" | "VEG" | "ZH":
                extensometer_data = update_extensometer_data_secondseries(
                    location, location_fullname, period=period
                )
            case "GDA" | "BKG" | "BKW" | "CBW" | "HZW":
                extensometer_data = update_extensometer_data_regiodeal(
                    location, location_fullname, period=period
                )

            case "M4T" | "MMW" | "MSW":
                extensometer_data = update_extensometer_data_moordrecht(
                    location, location_fullname, period=period
                )

    return extensometer_data


if __name__ == "__main__":

    # locations = ["VLI"]  # ["ALB", "ASD", "ROU", "VLI", "ZEG"]
    # locations = ["BKG"]
    # locations = ["DEM", "LW", "VEG", "ZH"]
    # locations = ["BKW"]  # "HZW", "BKG", "CBW", "HZW",
    # locations = ["ROU09"]

    locations = ["VEG"]  # ["M4T", "MMW"]

    # location_fullnames = {
    #     "ALB": "Aldeboarn",
    #     "ASD": "Assendelft",
    #     "ROU": "Rouveen",
    #     "VLI": "Vlist",
    #     "ZEG": "Zegveld",
    #     "DEM": "Demmerik",
    #     "LW": "LangeWeide",
    #     "VEG": "Vegelinsoord",
    #     "ZH": "ZegveldHoogwater",
    #     "LR": "LangRoggebroek",
    #     "GOU": "Gouda_MBORijnland",
    # }

    data = update_extensometer_data(locations)
