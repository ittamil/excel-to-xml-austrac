import time
from datetime import date, datetime,timedelta

def ConvertDateFormat(date_string):

    date_formats = ["%d-%m-%Y", "%m/%d/%Y", "%Y%m%d","%d.%m.%Y","%Y-%m-%d %H:%M:%S"]
    parsed_date = None
    for date_format in date_formats:
        try:
            parsed_date = datetime.strptime(str(date_string), date_format)
            break
        except ValueError:
            pass

    if parsed_date is not None:
        if date_format == "%d-%m-%Y":
            converted_date = datetime.strptime(str(date_string), "%d-%m-%Y").strftime("%Y-%m-%d")
        elif date_format == "%d.%m.%Y":
            converted_date = datetime.strptime(str(date_string), "%d.%m.%Y").strftime("%Y-%m-%d")
        elif date_format == "%Y-%m-%d %H:%M:%S":
            converted_date = datetime.strptime(str(date_string), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
        elif date_format == "%m/%d/%Y":
            converted_date = datetime.strptime(str(date_string), "%m/%d/%Y").strftime("%Y-%m-%d")
        elif date_format == "%Y%m%d":
            converted_date = datetime.strptime(str(date_string), "%Y%m%d").strftime("%Y-%m-%d")

        return converted_date    