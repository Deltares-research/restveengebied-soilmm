def subtract_value_in_januari(data):
    """
    Subtract the value on 1st January in the second year of data.
    """
    currentyear = data.first_valid_index().year
    nextyear = currentyear + 1
    reference_date = str(nextyear) + "-01-01"

    data = data - data.loc[reference_date].mean()

    return reference_date, data
