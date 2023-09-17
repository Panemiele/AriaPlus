import os
import pandas as pd
import aiohttp
import asyncio

openstreetmap_url_basepath = "http://nominatim.openstreetmap.org/reverse"
base_lat_lon_file_path = "C:\\Users\\Gabri\\lat-lon.csv"
new_lat_lon_file_path = "C:\\Users\\Gabri\\new-lat-lon.csv"


async def findCityByCoordinates(session, latitude, longitude):
    parameters = {
        'format': 'json',
        'lat': str(latitude),
        'lon': str(longitude)
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
    }
    async with session.get(openstreetmap_url_basepath, params=parameters, headers=headers) as response:
        return await response.json(content_type=None) if response.status == 200 else None

def getCityFromResponse(data):
    address = data.get('address', {})
    return address.get('city') or address.get('town', '---')

async def addCityToCsv(session, tuple, lat_lon_csv):
    response_data = await findCityByCoordinates(session, tuple[2], tuple[3])
    city = getCityFromResponse(response_data) if response_data is not None else "---"
    lat_lon_csv.at[tuple.Index, "city"] = city
    lat_lon_csv.to_csv(new_lat_lon_file_path, header=True, index=False)
    print(tuple.Index)


async def addCityToCsvWithSemaphore(session, tuple, lat_lon_csv, semaphore):
    async with semaphore:
        await addCityToCsv(session, tuple, lat_lon_csv)


async def main():
    if os.path.exists(new_lat_lon_file_path):
        os.remove(new_lat_lon_file_path)

    lat_lon_csv = pd.read_csv(base_lat_lon_file_path)
    lat_lon_csv["city"] = None

    semaphore = asyncio.Semaphore(10)  # Limite delle connessioni parallele

    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=300),
        connector=aiohttp.TCPConnector(limit=10)
    ) as session:
        tasks = [addCityToCsvWithSemaphore(session, t, lat_lon_csv, semaphore) for t in lat_lon_csv.itertuples()]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())