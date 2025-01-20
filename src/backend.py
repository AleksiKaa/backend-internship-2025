from fastapi import FastAPI
import asyncio
import aiohttp

app = FastAPI()


@app.get("/api")
def read_root():
    return {"Hello": "World"}


# http://localhost:8000/api/v1/delivery-order-price?venue_slug=home-assignment-venue-helsinki&cart_value=1000&user_lat=60.17094&user_lon=24.93087
@app.get("/api/v1/delivery-order-price")
async def get(venue_slug: str, cart_value: int, user_lat: float, user_lon: float):
    results = await get_venue_information(venue_slug)
    return results


def calculate_distance(user_coords: list[float], venue_coords: list[float]) -> float:
    """Calculate the straight line distance for two pairs of points"""
    x1, y1 = user_coords
    x2, y2 = venue_coords

    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


async def get_venue_information(venue_slug: str):
    uri = f"https://consumer-api.development.dev.woltapi.com/home-assignment-api/v1/venues/{venue_slug}"

    # Fetch data from external API
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{uri}/static") as static_response, session.get(
            f"{uri}/dynamic"
        ) as dynamic_response:
            if static_response.status != 200:
                return {"static": static_response.status}

            if dynamic_response.status != 200:
                return {"dynamic": dynamic_response.status}

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
