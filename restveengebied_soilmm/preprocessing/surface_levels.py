from pathlib import Path
import openpyxl
import csv


def write_surface_level(location, location_fullname, plot_type="RF"):

    if location == "HZW":
        filename = location_fullname.removesuffix("-Dorp")
    else:
        filename = location_fullname

    match location:
        case "ROU":
            basedir = Path(
                r"n:/Projects/11202000/11202008/B. Measurements and calculations/Extensometers"
            )
            path_to_data = basedir.joinpath("WDOD-05B-ref.xlsm")
        case "ROU09":
            basedir = Path(
                r"n:/Projects/11202000/11202008/B. Measurements and calculations/Extensometers"
            )
            if plot_type == "MS":
                path_to_data = basedir.joinpath("WDOD-09A-drain.xlsm")
            else:
                path_to_data = basedir.joinpath("WDOD-09B-ref.xlsm")
        case "ALB" | "ASD" | "VLI" | "ZEG":
            basedir = Path(
                r"n:/Projects/11204000/11204108/B. Measurements and calculations/Extensometers/"
            )
            path_to_data = basedir.joinpath(f"{location}_{plot_type}.xlsm")
        case "DEM" | "LW" | "VEG" | "ZH":
            basedir = Path(
                "n:/Projects/11206000/11206457/B. Measurements and calculations"
            )
            path_to_data = basedir.joinpath(
                location_fullname, "Extensometer", f"{filename}.xlsm"
            )
        case "GDA" | "BKW" | "BKG" | "CBW" | "HZW":
            basedir = Path(
                r"n:/Projects/11206000/11206020/B. Measurements and calculations"
            )
            path_to_data = basedir.joinpath("Extensometers", f"{filename}.xlsm")
        case "MMW" | "M4T" | "MSW":
            basedir = Path(
                r"n:/Projects/11210000/11210175/B. Measurements and calculations"
            )
            path_to_data = basedir.joinpath("Extensometers", f"{filename}.xlsm")

    if location == "ZEG":
        if plot_type == "MS":
            path_to_data = basedir.joinpath(f"{location}_003_perceel 16-drain.xlsm")

    match location:
        case "ROU" | "ROU09":
            column_row = "C56"
        case "ALB" | "ASD" | "VLI" | "ZEG" | "LW" | "VEG" | "ZH":
            column_row = "C21"
        case "DEM":
            column_row = "C27"
        case "GDA" | "BKW" | "BKG" | "CBW" | "HZW":
            column_row = "B23"
        case "M4T" | "MSW":
            column_row = "C108"
        case "MMW":
            column_row = "C109"

    outputdir = Path(
        r"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging/data/2-interim"
    )

    wb = openpyxl.load_workbook(path_to_data, read_only=True)
    print("Workbook loaded")
    sheet = wb["cal"]  # .active

    surface_level = sheet[column_row].value

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
            plot_type = ""
        case _:
            plot_type = "_" + plot_type

    with open(
        outputdir.joinpath(
            location_fullname, f"{location}_surface_level{plot_type}.csv"
        ),
        "w+",
        encoding="UTF8",
    ) as f:

        writer = csv.writer(f)

        writer.writerows([[surface_level]])


if __name__ == "__main__":

    from restveengebied_soilmm.constants import LOCATION_FULLNAMES

    # locations = ["ROU09"]  # ["ROU", "VLI", "ZEG"]
    locations = ["MSW"]

    # LOCATION_FULLNAMES = {
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
    # }

    for location in locations:

        location_fullname = LOCATION_FULLNAMES[location]

        print(f"Analyzing the surface level of {location_fullname}")

        write_surface_level(location, location_fullname, plot_type="RF")
