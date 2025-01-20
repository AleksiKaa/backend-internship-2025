from fastapi import FastAPI
import asyncio
import aiohttp

app = FastAPI()


@app.get("/api")
def read_root():
    return {"Hello": "World"}


@app.get("/api/v1/delivery-order-price")
async def get(venue_slug: str, cart_value: int, user_lat: float, user_lon: float):
    results = await get_venue_information(venue_slug)
    user_coords = [user_lat, user_lon]
    order_info = calculate_price(results, cart_value, user_coords)
    return order_info


def calculate_distance(user_coords: list[float], venue_coords: list[float]) -> int:
    """Calculate the straight line distance for two pairs of points"""
    x1, y1 = user_coords
    x2, y2 = venue_coords

    return int(((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5)


def calculate_delivery_fee(base_price: int, a: int, b: int, distance: float) -> int:
    """Formula for calculating the delivery fee"""
    return base_price + a + b * distance // 10


def calculate_price(
    venue_information: dict, cart_value: int, user_coords: list[int]
) -> {}:
    """Calculate the price of the order according to assignment specifications"""
    base_price, order_minimum_no_surcharge, venue_coords = (
        venue_information["base_price"],
        venue_information["order_minimum_no_surcharge"],
        venue_information["coordinates"],
    )

    dist = calculate_distance(user_coords, venue_coords)
    for dist_range in venue_information["distance_ranges"]:
        if dist >= dist_range["min"] and dist < dist_range["max"]:
            delivery_fee = calculate_delivery_fee(
                base_price, dist_range["a"], dist_range["b"], dist
            )

    small_order_surcharge = max(cart_value - order_minimum_no_surcharge, 0)
    order_info = {
        "total_price": cart_value + small_order_surcharge + delivery_fee,
        "small_order_surcharge": small_order_surcharge,
        "cart_value": cart_value,
        "delivery": {"fee": delivery_fee, "distance": dist},
    }
    return order_info


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
