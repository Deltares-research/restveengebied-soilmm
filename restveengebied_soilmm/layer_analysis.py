import pandas as pd
from scipy import signal


def calculate_layer_thickness(extensometer_data):

    column_names = [
        f"{extensometer_data.columns[col+1]} - {extensometer_data.columns[col]}"
        for col in range(len(extensometer_data.columns) - 1)
    ]

    column_names = [column_name.replace("m-mv", "m bs") for column_name in column_names]

    layer_thickness = extensometer_data.diff(axis=1) * -1
    layer_thickness = layer_thickness.drop(layer_thickness.columns[0], axis=1)
    layer_thickness.columns = column_names

    return layer_thickness


def detrend_layers(layer_thickness_data, detrend_method="linear", window_length=7):

    detrended_layers = pd.DataFrame()

    for column in layer_thickness_data.columns:

        if detrend_method == "linear":
            detrended_layer = signal.detrend(layer_thickness_data[column])
        elif detrend_method == "moving_average":
            detrended_layer = (
                layer_thickness_data[column]
                - layer_thickness_data[column].rolling(window_length).mean()
            )
        else:
            raise ValueError("Invalid detrend method.")

        detrended_layer = pd.Series(
            detrended_layer, index=layer_thickness_data.index, name=column
        )

        if detrended_layers.empty:
            detrended_layers = detrended_layer.to_frame()
        else:
            detrended_layers = pd.concat([detrended_layers, detrended_layer], axis=1)

    return detrended_layers


def calculate_layer_thickness_start(soilprofile_anchors, column_names):
    layer_thickness_start = soilprofile_anchors.diff().dropna()

    layer_thickness_start.index = (
        column_names  # use the same index as the layer thickness data
    )

    layer_thickness_start *= 100  # convert to cm
    layer_thickness_start *= -1  # invert the values to get the correct direction

    layer_thickness_start = layer_thickness_start.to_frame(name="laagdiktes")
    layer_thickness_start.columns = pd.MultiIndex.from_product([[""], ["laagdiktes"]])

    return layer_thickness_start


def calculate_anchor_depth_start(soilprofile_anchors, column_names):
    # calculate the anchor depth start
    anchor_depth_start = soilprofile_anchors.copy()

    # set the index to the column names of the layer thickness data
    anchor_depth_start.index = column_names

    # convert to cm
    anchor_depth_start *= 100

    # invert the values to get the correct direction
    # anchor_depth_start *= -1

    return anchor_depth_start


def calculate_rek(layer_thickness, layer_thickness_start):
    # calculate the deformation in cm
    totale_deformatie = layer_thickness  # + layer_thickness_start.T.values

    # calculate the rek
    rek = totale_deformatie / layer_thickness_start.T.values

    return totale_deformatie, rek


if __name__ == "__main__":

    from nobv_soilmm.read import read_extensometer, read_soilprofile
    from nobv_soilmm.constants import LOCATION_FULLNAMES

    location = "ZEG"

    extensometer_data = read_extensometer(location)
    _, soilprofile_anchors = read_soilprofile(location, LOCATION_FULLNAMES[location])

    layer_thickness = calculate_layer_thickness(extensometer_data)

    # layer_thickness_detrended = detrend_layers(layer_thickness, detrend_method="linear")

    layer_thickness_start = calculate_layer_thickness_start(
        soilprofile_anchors=soilprofile_anchors["m-mv"],
        column_names=layer_thickness.columns,
    )

    totale_deformatie, rek = calculate_rek(
        layer_thickness=layer_thickness, layer_thickness_start=layer_thickness_start
    )

    anchor_depth_start = calculate_anchor_depth_start(
        soilprofile_anchors=soilprofile_anchors["m NAP"],
        column_names=extensometer_data.columns,
    )
