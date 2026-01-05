from pathlib import Path
import openpyxl
import csv


def write_filter_depths(location, location_fullname, columns, plot_type="RF"):

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

    match location:
        case "GDA" | "BKW" | "BKG" | "CBW" | "HZW":
            row_top_filter = 27
            row_bottom_filter = 28
        case "M4T" | "MSW":
            row_top_filter = 32
            row_bottom_filter = 33
        case "MMW":
            row_top_filter = 33
            row_bottom_filter = 34

    outputdir = Path(
        r"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging/data/2-interim"
    )

    wb = openpyxl.load_workbook(path_to_data, read_only=True, data_only=True)
    print("Workbook loaded")
    sheet = wb["cal"]  # .active

    top_filter_levels = []
    bottom_filter_levels = []

    for i, column in enumerate(columns):
        top_filter_level = sheet[f"{column}{row_top_filter}"].value
        bottom_filter_level = sheet[f"{column}{row_bottom_filter}"].value

        top_filter_levels.append(top_filter_level)
        bottom_filter_levels.append(bottom_filter_level)

    # pass

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
            location_fullname, f"{location}_filterdepths{plot_type}.csv"
        ),
        "w+",
        encoding="UTF8",
        newline="",
    ) as f:

        writer = csv.writer(f)
        writer.writerows(zip(top_filter_levels, bottom_filter_levels))


if __name__ == "__main__":

    from restveengebied_soilmm.constants import LOCATION_FULLNAMES

    # locations = ["ROU09"]  # ["ROU", "VLI", "ZEG"]
    # locations = ["GDA", "BKG", "BKW", "CBW", "HZW"]
    locations = ["M4T", "MMW", "MSW"]
    # locations = ["M4T"]
    columns = [["B", "C", "D"], ["B", "C", "D", "E"], ["B", "C", "D", "E"]]
    # locations = ["VEG"]

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

    for i, location in enumerate(locations):

        location_fullname = LOCATION_FULLNAMES[location]

        print(f"Analyzing the surface level of {location_fullname}")

        # write_filter_depth_phreatic(location, location_fullname, plot_type="RF")
        # write_filter_depth_hydraulic_head(location, location_fullname, plot_type="RF")
        write_filter_depths(location, location_fullname, columns=columns[i])
