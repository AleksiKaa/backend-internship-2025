from fastapi import FastAPI
import asyncio
import aiohttp

app = FastAPI()


@app.get("/api")
def read_root():
    return {"Hello": "World"}


# http://localhost:8000/api/v1/delivery-order-price?venue_slug=home-assignment-venue-helsinki&cart_value=1000&user_lat=60.17094&user_lon=24.93087
@app.get("/api/v1/delivery-order-price")
def get(venue_slug: str, cart_value: int, user_lat: float, user_lon: float):
    return {"a": venue_slug, "b": cart_value, "c": user_lat, "d": user_lon}


# All the money related information (prices, fees, etc) are in the lowest denomination of the local currency.
# In euro countries they are in cents, in Sweden they are in öre, and in Japan they are in yen.


def get_venue_information(venue_slug: str, static: bool = True):
    pass
