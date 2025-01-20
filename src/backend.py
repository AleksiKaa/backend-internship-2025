from utils import calculate_price

from fastapi import FastAPI
import aiohttp

app = FastAPI()


@app.get("/api/v1/delivery-order-price")
async def get(venue_slug: str, cart_value: int, user_lat: float, user_lon: float):
    venue_info = await get_venue_information(venue_slug)
    user_coords = [user_lat, user_lon]
    order_price = calculate_price(venue_info, cart_value, user_coords)
    return order_price


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
