import os
import time

import pandas as pd
import requests

openstreetmap_url_basepath = "http://nominatim.openstreetmap.org/reverse"
base_lat_lon_file_path = "C:\\Users\\Gabri\\lat-lon.csv"
new_lat_lon_file_path = "C:\\Users\\Gabri\\new-lat-lon.csv"


def findCityByCoordinates(latitude, longitude):
    parameters = {
        'format': 'json',
        'lat': str(latitude),
        'lon': str(longitude)
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
    }
    response = requests.get(openstreetmap_url_basepath, params=parameters, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None


def getCityFromResponse(data):
    address = data.get('address', {})
    return address.get('city') or address.get('town', '---')


def addCityToCsv(tuple, lat_lon_csv):
    print(tuple.Index)
    response_data = findCityByCoordinates(tuple[2], tuple[3])
    city = getCityFromResponse(response_data) if response_data is not None else "---"
    lat_lon_csv.at[tuple.Index, "city"] = city
    lat_lon_csv.to_csv(new_lat_lon_file_path, header=True, index=False)


def main():
    if os.path.exists(new_lat_lon_file_path):
        os.remove(new_lat_lon_file_path)

    lat_lon_csv = pd.read_csv(base_lat_lon_file_path)
    lat_lon_csv["city"] = None

    for t in lat_lon_csv.itertuples():
        addCityToCsv(t, lat_lon_csv)
        time.sleep(1)


if __name__ == "__main__":
    main()