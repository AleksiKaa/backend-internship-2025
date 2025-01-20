from typing import Dict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import aiohttp

from utils import calculate_price


class WoltException(Exception):
    def __init__(self, content: Dict):
        self.content = content


app = FastAPI()


@app.exception_handler(WoltException)
async def wolt_exception_handler(request: Request, exc: WoltException):
    return JSONResponse(
        status_code=400,
        content=exc.content,
    )


@app.get("/api/v1/delivery-order-price", status_code=200)
async def get(venue_slug: str, cart_value: int, user_lat: float, user_lon: float):
    venue_info = await get_venue_information(venue_slug)

    if not venue_info:
        raise WoltException(content={"message": "Problem fetching venue info."})

    user_coords = [user_lat, user_lon]
    order_price = calculate_price(venue_info, cart_value, user_coords)

    if not order_price:
        raise WoltException(content={"message": "No suitable delivery option. Distance too large."})

    return JSONResponse(content=order_price, status_code=200)


async def get_venue_information(venue_slug: str):
    uri = f"https://consumer-api.development.dev.woltapi.com/home-assignment-api/v1/venues/{venue_slug}"

    # Fetch data from external API
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{uri}/static") as static_response, session.get(
            f"{uri}/dynamic"
        ) as dynamic_response:
            if static_response.status != 200:
                return {}

            if dynamic_response.status != 200:
                return {}

            data_static = await static_response.json()
            data_dynamic = await dynamic_response.json()
            # Fetch relevant fields from data
            results = {
                "coordinates": data_static["venue_raw"]["location"]["coordinates"],
                "order_minimum_no_surcharge": data_dynamic["venue_raw"][
                    "delivery_specs"
                ]["order_minimum_no_surcharge"],
                "base_price": data_dynamic["venue_raw"]["delivery_specs"][
                    "delivery_pricing"
                ]["base_price"],
                "distance_ranges": data_dynamic["venue_raw"]["delivery_specs"][
                    "delivery_pricing"
                ]["distance_ranges"],
            }

            return results
