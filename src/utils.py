from typing import Dict


def calculate_distance(user_coords: list[float], venue_coords: list[float]) -> int:
    """Calculate the straight line distance for two pairs of points"""
    x1, y1 = user_coords
    x2, y2 = venue_coords

    return round(((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5)


def calculate_delivery_fee(base_price: int, a: int, b: int, distance: float) -> int:
    """Formula for calculating the delivery fee"""
    return base_price + a + b * distance // 10


def calculate_price(
    venue_information: dict, cart_value: int, user_coords: list[int]
) -> Dict:
    """Calculate the price of the order according to assignment specifications"""
    base_price, order_minimum_no_surcharge, venue_coords = (
        venue_information["base_price"],
        venue_information["order_minimum_no_surcharge"],
        venue_information["coordinates"],
    )

    # Loop over ranges to find a suitable one
    dist = calculate_distance(user_coords, venue_coords)
    for dist_range in venue_information["distance_ranges"]:
        if dist_range["min"] <= dist < dist_range["max"]:
            # Suitable range found, calculate values of importance
            delivery_fee = calculate_delivery_fee(
                base_price, dist_range["a"], dist_range["b"], dist
            )

            small_order_surcharge = max(order_minimum_no_surcharge - cart_value, 0)
            order_info = {
                "total_price": cart_value + small_order_surcharge + delivery_fee,
                "small_order_surcharge": small_order_surcharge,
                "cart_value": cart_value,
                "delivery": {"fee": delivery_fee, "distance": dist},
            }
            return order_info

    # No suitable delivery option, return empty dict
    return {}
