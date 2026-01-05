def subtract_value_at_levelling_date(data, levelling_date):
    data = data - data.loc[levelling_date].mean()

    return data
