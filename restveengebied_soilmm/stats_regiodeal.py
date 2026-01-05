import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import dates as mdates
from pathlib import Path
import scipy

from nobv_soilmm.constants import MONTHS


def calculate_dynamic(extensometer_year, year):
    extensometer_min = extensometer_year.min(axis=0)  # .to_frame(name='min')
    extensometer_max = extensometer_year.max(axis=0)  # .to_frame(name='max')
    dynamiek_jaar = extensometer_max - extensometer_min  # .to_frame(name='dynamiek')

    yearly_dynamics = pd.concat(
        [extensometer_min, extensometer_max, dynamiek_jaar],
        axis=1,
        names=["min", "max", "dynamiek"],
    )
    yearly_dynamics.columns = pd.MultiIndex.from_product(
        [[year], ["min", "max", "dynamiek"]]
    )

    return yearly_dynamics


def calculate_deformation(layer_thickness_year, year):
    layer_thickness_min = layer_thickness_year.min(axis=0)  # .to_frame(name='min')
    layer_thickness_max = layer_thickness_year.max(axis=0)  # .to_frame(name='max')
    dynamiek_jaar = (
        layer_thickness_max - layer_thickness_min
    )  # .to_frame(name='dynamiek')

    yearly_dynamics = pd.concat(
        [layer_thickness_min, layer_thickness_max, dynamiek_jaar],
        axis=1,
    )

    yearly_dynamics.columns = pd.MultiIndex.from_product(
        [[year], ["min", "max", "totale deformatie"]]
    )

    return yearly_dynamics


def get_trendline(extensometer_data, months=(1, 2)):

    highest_per_year = (
        extensometer_data[extensometer_data.index.month.isin(months)]
        .resample("h")
        .mean()
    )

    highest_per_year.dropna(inplace=True)

    x = mdates.date2num(highest_per_year.index)
    y = highest_per_year.values

    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)

    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, y)
    r_2 = r_value * r_value

    # convert slope to mm/year
    slope *= 365.25

    # cm/year to mm/year
    slope *= 10

    return p, x, r_2, slope


if __name__ == "__main__":

    from read import read_extensometer, read_soilprofile, read_soilprofile_regiodeal
    from constants import LOCATION_FULLNAMES, EXTENSOMETER_DEPTHS, SOILPROFILE_DEPTHS

    from nobv_soilmm.layer_analysis import (
        calculate_layer_thickness,
        calculate_rek,
    )

    #################################################################
    # Parameters
    #################################################################

    locations = ["GDA", "BKG", "BKW", "CBW", "HZW"]
    # locations = ["HZW"]

    write_yearly_stats = False
    write_trendline_stats = True

    trendline_months = (1, 2)

    basedir = Path(
        f"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging/data"
    )

    if write_yearly_stats:

        info_sheet = pd.read_excel(
            basedir.joinpath(r"2-interim", "info_sheet_jaarlijkse_statistieken.xlsx"),
            index_col=0,
            header=3,
        )

        ## prepare Excel file
        writer = pd.ExcelWriter(
            basedir.joinpath("4-output", "jaarlijkse_statistieken_regiodeal.xlsx"),
            engine="xlsxwriter",
        )
        info_sheet.to_excel(writer, startrow=3, sheet_name=r"info sheet")
        for i, width in enumerate([44, 60, 60, 34]):
            writer.sheets["info sheet"].set_column(i, i, width)

        worksheet = writer.sheets["info sheet"]
        worksheet.write(0, 0, "Uitleg statistieken bodembeweging")
        worksheet.write(
            1,
            0,
            "De statistieken zijn berekend vanaf 1 november het jaar ervoor tm 31 oktober in het jaar zelf",
        )

    if write_trendline_stats:

        info_sheet = pd.read_excel(
            basedir.joinpath(r"2-interim", "info_sheet_trendlijn_statistieken.xlsx"),
            index_col=0,
            header=3,
        )

        ## prepare Excel file
        writer_trendline = pd.ExcelWriter(
            basedir.joinpath("4-output", "trendlijn_statistieken_regiodeal.xlsx"),
            engine="xlsxwriter",
        )
        info_sheet.to_excel(writer_trendline, startrow=3, sheet_name=r"info sheet")
        for i, width in enumerate([44, 100, 40]):
            writer_trendline.sheets["info sheet"].set_column(i, i, width)

        worksheet_trendline = writer_trendline.sheets["info sheet"]
        worksheet_trendline.write(0, 0, "Uitleg trendlijn statistieken bodembeweging")

        worksheet_trendline.write(
            1,
            0,
            f"De trendlijn is berekend over de volgende maanden: {[MONTHS[i] for i in trendline_months]}",
        )

    for location in locations:
        location_fullname = LOCATION_FULLNAMES[location]

        print(f"Analyzing stats for location: {location_fullname}")

        #################################################################
        # read data
        #################################################################

        extensometer_data = read_extensometer(location)

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
            _, soilprofile_anchors = read_soilprofile(location, location_fullname)
        elif location in ["GDA"]:
            _, soilprofile_anchors = read_soilprofile_regiodeal(
                location, location_fullname
            )
        else:
            extensometer_depth = EXTENSOMETER_DEPTHS[location]

            anchor_levels = []

            for i, soilprofile_anchor in enumerate(extensometer_depth):
                anchor_levels.append(-1 * float(soilprofile_anchor.split(" ")[0]))

            soilprofile_anchors = pd.DataFrame(
                anchor_levels, index=extensometer_data.columns, columns=["m-mv"]
            )
            # anchor_depth_start = calculate_anchor_depth_start(
        #     soilprofile_anchors=soilprofile_anchors["m NAP"],
        #     column_names=extensometer_data.columns,
        # )
        # anchor_depth_start = anchor_depth_start.to_frame(name="ankerdiepte")
        # anchor_depth_start.columns = pd.MultiIndex.from_product([[""], ["ankerdiepte"]])

        # extensometer_data -= (
        #     anchor_depth_start.T.values
        # )  # add the anchor depth to the data
        ################################################################
        # calculate layer thicknesses
        ################################################################

        layer_thickness_data = calculate_layer_thickness(extensometer_data)
        layer_thickness_start = soilprofile_anchors["m-mv"].diff().dropna()

        layer_thickness_start.index = (
            layer_thickness_data.columns
        )  # use the same index as the layer thickness data

        layer_thickness_start *= 100  # convert to cm
        layer_thickness_start *= -1  # invert the values to get the correct direction

        layer_thickness_start = layer_thickness_start.to_frame(name="laagdiktes")
        layer_thickness_start.columns = pd.MultiIndex.from_product(
            [[""], ["laagdiktes"]]
        )

        ################################################################
        # calculate rek
        ################################################################

        _, rek = calculate_rek(layer_thickness_data, layer_thickness_start)

        #################################################################
        # output directory
        #################################################################

        outputdir = Path(
            f"n:/Projects/11211000/11211391/B. Measurements and calculations/Bodembeweging/data/4-output"
        )

        ################################################################
        # calculate yearly stats
        ################################################################
        if write_yearly_stats:

            years = extensometer_data.index.year.unique()

            yearly_stats = pd.DataFrame()
            yearly_stats_layer_thickness = pd.DataFrame()

            for year in years:
                # print(f"Analysing year {year}")

                start = pd.to_datetime(f"{year-1}-11-01")
                end = pd.to_datetime(f"{year}-10-31")

                if (
                    (start in extensometer_data.index)
                    and (end in extensometer_data.index)
                ) or (year == 2022):
                    extensometer_year = extensometer_data.loc[start:end]
                    layer_thickness_year = layer_thickness_data.loc[start:end]
                    rek_year = rek.loc[start:end]

                    dynamiek_jaar = calculate_dynamic(extensometer_year, year)
                    dynamiek_jaar_layer_thickness = calculate_deformation(
                        layer_thickness_year, year
                    )

                    # print(dynamiek_jaar_layer_thickness)

                    # add the starting layer thickness using pd.add
                    # see https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.add.html
                    # this is also available for divisions and subtractions
                    dynamiek_jaar_layer_thickness.iloc[:, :2] = (
                        dynamiek_jaar_layer_thickness.iloc[:, :2].add(
                            layer_thickness_start.values, axis="index"
                        )
                    )

                    # dynamiek_jaar.iloc[:, :2] = dynamiek_jaar.iloc[:, :2].add(
                    #     anchor_depth_start.values, axis="index"
                    # )

                    totale_deformatie = dynamiek_jaar_layer_thickness.iloc[
                        :,
                        dynamiek_jaar_layer_thickness.columns.get_level_values(1)
                        == "totale deformatie",
                    ]

                    dynamiek_jaar_layer_thickness[year, "rek"] = (
                        totale_deformatie / layer_thickness_start.values
                    )

                    dynamiek_jaar[year, "percent of upper anchor dynamic (%)"] = (
                        dynamiek_jaar[year, "dynamiek"]
                        / dynamiek_jaar.loc[dynamiek_jaar.index[0]][year, "dynamiek"]
                        * 100
                    )

                    # dynamiek_jaar_layer_thickness[year, "rek"] = (
                    #     rek_year.abs().max(axis=0)
                    # )

                    if yearly_stats.empty:
                        yearly_stats = dynamiek_jaar
                    else:
                        yearly_stats = pd.concat([yearly_stats, dynamiek_jaar], axis=1)

                    if yearly_stats_layer_thickness.empty:
                        yearly_stats_layer_thickness = dynamiek_jaar_layer_thickness
                    else:
                        yearly_stats_layer_thickness = pd.concat(
                            [
                                yearly_stats_layer_thickness,
                                dynamiek_jaar_layer_thickness,
                            ],
                            axis=1,
                        )

            # yearly_stats = pd.concat([anchor_depth_start, yearly_stats], axis=1)
            yearly_stats_layer_thickness = pd.concat(
                [
                    layer_thickness_start,
                    yearly_stats_layer_thickness,
                ],
                axis=1,
            )

            # round results
            # yearly_stats = yearly_stats.round(2)
            yearly_stats.iloc[:, yearly_stats.columns.get_level_values(1) == "min"] = (
                yearly_stats.iloc[
                    :, yearly_stats.columns.get_level_values(1) == "min"
                ].round(2)
            )

            yearly_stats.iloc[:, yearly_stats.columns.get_level_values(1) == "max"] = (
                yearly_stats.iloc[
                    :, yearly_stats.columns.get_level_values(1) == "max"
                ].round(2)
            )

            yearly_stats.iloc[
                :, yearly_stats.columns.get_level_values(1) == "dynamiek"
            ] = yearly_stats.iloc[
                :, yearly_stats.columns.get_level_values(1) == "dynamiek"
            ].round(
                2
            )

            yearly_stats.iloc[
                :,
                yearly_stats.columns.get_level_values(1)
                == "percent of upper anchor dynamic (%)",
            ] = yearly_stats.iloc[
                :,
                yearly_stats.columns.get_level_values(1)
                == "percent of upper anchor dynamic (%)",
            ].round(
                1
            )

            yearly_stats_layer_thickness.iloc[
                :, yearly_stats_layer_thickness.columns.get_level_values(1) == "min"
            ] = yearly_stats_layer_thickness.iloc[
                :, yearly_stats_layer_thickness.columns.get_level_values(1) == "min"
            ].round(
                2
            )
            yearly_stats_layer_thickness.iloc[
                :, yearly_stats_layer_thickness.columns.get_level_values(1) == "max"
            ] = yearly_stats_layer_thickness.iloc[
                :, yearly_stats_layer_thickness.columns.get_level_values(1) == "max"
            ].round(
                2
            )
            yearly_stats_layer_thickness.iloc[
                :,
                yearly_stats_layer_thickness.columns.get_level_values(1)
                == "totale deformatie",
            ] = yearly_stats_layer_thickness.iloc[
                :,
                yearly_stats_layer_thickness.columns.get_level_values(1)
                == "totale deformatie",
            ].round(
                3
            )
            yearly_stats_layer_thickness.iloc[
                :,
                yearly_stats_layer_thickness.columns.get_level_values(1) == "rek",
            ] = yearly_stats_layer_thickness.iloc[
                :,
                yearly_stats_layer_thickness.columns.get_level_values(1) == "rek",
            ].round(
                4
            )

            yearly_stats.to_excel(writer, sheet_name=location_fullname, startrow=1)
            yearly_stats_layer_thickness.to_excel(
                writer,
                sheet_name=location_fullname,
                startrow=7 + len(extensometer_data.columns),
            )

            # set column width of index column
            writer.sheets[location_fullname].set_column(0, 0, 23)

            worksheet = writer.sheets[location_fullname]
            worksheet.write(
                0, 0, f"Jaarlijkse statistieken extensometer {location_fullname} (cm)"
            )
            worksheet.write(
                6 + len(extensometer_data.columns),
                0,
                f"Jaarlijkse statistieken laagdiktes {location_fullname} (cm)",
            )

            # set column width of all columns with 'totale deformatie'
            mask = yearly_stats_layer_thickness.columns.get_level_values(1).isin(
                ["totale deformatie"]
            )
            idxs = np.arange(len(yearly_stats_layer_thickness.columns))
            selected_idxs = idxs[mask]

            for idx in selected_idxs:
                writer.sheets[location_fullname].set_column(idx + 1, idx + 1, 30)

            # set column width of all columns with 'totale deformatie'
            mask = yearly_stats.columns.get_level_values(1).isin(
                ["percent of upper anchor dynamic (%)"]
            )
            idxs = np.arange(len(yearly_stats.columns))
            selected_idxs = idxs[mask]

            for idx in selected_idxs:
                writer.sheets[location_fullname].set_column(idx + 1, idx + 1, 40)

            # set the column width of the laagdiktes column
            writer.sheets[location_fullname].set_column(1, 1, 15)

        ################################################################
        # get trendline stats
        ################################################################

        if write_trendline_stats:

            if location in ["BKG"]:
                nr_of_loops = 3
                start_dates = [
                    extensometer_data.index[0],
                    pd.to_datetime("2023-11-05"),
                    extensometer_data.index[0],
                ]
                end_dates = [
                    pd.to_datetime("2023-09-14"),
                    extensometer_data.index[-1],
                    extensometer_data.index[-1],
                ]
                startrows = [3, 13, 23]

            else:
                nr_of_loops = 1
                start_dates = [extensometer_data.index[0]]
                end_dates = [extensometer_data.index[-1]]
                startrows = [2]

            for i in range(nr_of_loops):

                extensometer_data_period = extensometer_data.loc[
                    start_dates[i] : end_dates[i]
                ]
                layer_thickness_data_period = layer_thickness_data.loc[
                    start_dates[i] : end_dates[i]
                ]

                trendline_data = pd.DataFrame()
                trendline_data_layer_thickness = pd.DataFrame()

                # for location Langeweide (LW) we only want to use
                # the data from 2023
                # if location == "LW":
                #     extensometer_data = extensometer_data.loc["2023":]
                #     layer_thickness_data = layer_thickness_data.loc["2023":]

                for anchor in extensometer_data_period:
                    # print(f"Analysing anchor {anchor}")

                    # if (location == "HZW") and (anchor == "260 cm bs"):
                    #     continue

                    p, x, r2, slope = get_trendline(
                        extensometer_data_period[anchor], months=trendline_months
                    )

                    # print(f"R2 = {r2}")
                    # print(f"Slope = {slope}")

                    if trendline_data.empty:
                        trendline_data = pd.DataFrame(
                            data={anchor: [slope, r2]},
                            index=["Slope (mm/jaar)", "R2"],
                        )
                    else:
                        trendline_data[anchor] = [slope, r2]

                for layer in layer_thickness_data_period:

                    p, x, r2, slope = get_trendline(
                        layer_thickness_data_period[layer], months=trendline_months
                    )

                    if trendline_data_layer_thickness.empty:
                        trendline_data_layer_thickness = pd.DataFrame(
                            data={layer: [slope, r2]},
                            index=["Slope (mm/jaar)", "R2"],
                        )
                    else:
                        trendline_data_layer_thickness[layer] = [slope, r2]

                trendline_data = trendline_data.T
                trendline_data_layer_thickness = trendline_data_layer_thickness.T

                trendline_data["Contribution to subsidence (%)"] = (
                    trendline_data["Slope (mm/jaar)"]
                    / trendline_data.loc[trendline_data.index[0]]["Slope (mm/jaar)"]
                    * 100
                )

                trendline_data["R2"] = trendline_data["R2"].round(2)
                trendline_data["Slope (mm/jaar)"] = trendline_data[
                    "Slope (mm/jaar)"
                ].round(2)
                trendline_data["Contribution to subsidence (%)"] = trendline_data[
                    "Contribution to subsidence (%)"
                ].round(1)

                trendline_data_layer_thickness["Contribution to subsidence (%)"] = (
                    trendline_data_layer_thickness["Slope (mm/jaar)"]
                    / trendline_data.loc[trendline_data.index[0]]["Slope (mm/jaar)"]
                    * 100
                )
                trendline_data_layer_thickness["Layer thickness (cm)"] = [
                    int(lt.split(" ")[0]) - int(lt.split(" ")[4])
                    for lt in trendline_data_layer_thickness.index
                ]
                trendline_data_layer_thickness["Strain"] = (
                    trendline_data_layer_thickness["Slope (mm/jaar)"]
                    / (trendline_data_layer_thickness["Layer thickness (cm)"] * 10)
                )

                trendline_data_layer_thickness["R2"] = trendline_data_layer_thickness[
                    "R2"
                ].round(2)
                trendline_data_layer_thickness["Slope (mm/jaar)"] = (
                    trendline_data_layer_thickness["Slope (mm/jaar)"].round(2)
                )
                trendline_data_layer_thickness["Contribution to subsidence (%)"] = (
                    trendline_data_layer_thickness[
                        "Contribution to subsidence (%)"
                    ].round(1)
                )
                trendline_data_layer_thickness["Strain"] = (
                    trendline_data_layer_thickness["Strain"].round(4)
                )

                trendline_data.to_excel(
                    writer_trendline,
                    sheet_name=location_fullname,
                    startrow=startrows[i],
                )

                trendline_data_layer_thickness.to_excel(
                    writer_trendline,
                    sheet_name=location_fullname,
                    startrow=startrows[i],
                    startcol=5,
                )

            worksheet = writer_trendline.sheets[location_fullname]
            worksheet.write(
                0,
                0,
                f"Trendlijn statistieken extensometer ankers {location_fullname}",
            )

            worksheet.write(
                0,
                5,
                f"Trendlijn statistieken extensometer intervallen {location_fullname}",
            )

            if location in ["BKG"]:
                worksheet.write(
                    2,
                    0,
                    "Periode tot 14 september 2023",
                )

                worksheet.write(
                    2,
                    5,
                    "Periode tot 14 september 2023",
                )

                worksheet.write(
                    12,
                    0,
                    "Periode vanaf 5 november 2023",
                )

                worksheet.write(
                    12,
                    5,
                    "Periode vanaf 5 november 2023",
                )

                worksheet.write(
                    22,
                    0,
                    "Hele periode",
                )

                worksheet.write(
                    22,
                    5,
                    "Hele periode",
                )

            # set column width of index column
            writer_trendline.sheets[location_fullname].set_column(0, 0, 15)
            writer_trendline.sheets[location_fullname].set_column(5, 5, 23)

            # set column width of slope column
            writer_trendline.sheets[location_fullname].set_column(1, 1, 23)
            writer_trendline.sheets[location_fullname].set_column(6, 6, 23)

            # set column width of column: contribution to subsidence
            writer_trendline.sheets[location_fullname].set_column(3, 3, 30)
            writer_trendline.sheets[location_fullname].set_column(8, 8, 30)

            # set column width for the column: initial thickness
            # set column width of column: contribution to subsidence
            writer_trendline.sheets[location_fullname].set_column(9, 9, 30)
            writer_trendline.sheets[location_fullname].set_column(10, 10, 10)

    if write_yearly_stats:
        writer.close()

    if write_trendline_stats:
        writer_trendline.close()
