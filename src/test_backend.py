from fastapi.testclient import TestClient

from backend import app
from utils import calculate_distance, calculate_delivery_fee, calculate_price

client = TestClient(app)

test_uris = [
    "http://localhost:8000/api/v1/delivery-order-price?venue_slug=home-assignment-venue-helsinki&cart_value=1000&user_lat=60.17094&user_lon=24.93087",
]

test_db = [
    {
        "coordinates": [24.92813512, 60.17012143],
        "order_minimum_no_surcharge": 1000,
        "base_price": 190,
        "distance_ranges": [
            {"min": 0, "max": 500, "a": 0, "b": 0.0, "flag": None},
            {"min": 500, "max": 1000, "a": 100, "b": 0.0, "flag": None},
            {"min": 1000, "max": 1500, "a": 200, "b": 0.0, "flag": None},
            {"min": 1500, "max": 2000, "a": 200, "b": 1.0, "flag": None},
            {"min": 2000, "max": 0, "a": 0, "b": 0.0, "flag": None},
        ],
    },
    {
        "coordinates": [13.4536149, 52.5003197],
        "order_minimum_no_surcharge": 1000,
        "base_price": 190,
        "distance_ranges": [
            {"min": 0, "max": 500, "a": 0, "b": 0.0, "flag": None},
            {"min": 500, "max": 1000, "a": 100, "b": 0.0, "flag": None},
            {"min": 1000, "max": 1500, "a": 200, "b": 0.0, "flag": None},
            {"min": 1500, "max": 2000, "a": 200, "b": 1.0, "flag": None},
            {"min": 2000, "max": 0, "a": 0, "b": 0.0, "flag": None},
        ],
    },
]


def test_get_valid_response():
    response = client.get(test_uris[0])
    # Correct status code
    assert response.status_code == 200
    # Response has all required fields
    assert all(
        key in ["total_price", "small_order_surcharge", "cart_value", "delivery"]
        for key in response.json().keys()
    )
    assert all(key in ["fee", "distance"] for key in response.json()["delivery"].keys())


def test_calculate_distance():
    # Sanity checks
    assert calculate_distance([0, 0], [0, 0]) == 0
    assert calculate_distance([1, 1], [1, -1]) > 0
    assert calculate_distance([0, 0], [3, 4]) == 5


def test_calculate_delivery_fee():
    # Sanity checks
    assert calculate_delivery_fee(0, 0, 0, 0) == 0
    assert calculate_delivery_fee(100, 0, 0, 0) == 100
    assert calculate_delivery_fee(99, 1, 2, 50) == 110


def test_calculate_price_fail():
    assert calculate_price(test_db[0], 100, [10000, 10000]) == {}


def test_calculate_price_success():
    res = calculate_price(test_db[0], 1000, [200, 200])
    total_price, small_order_surcharge, cart_value, delivery = res.values()
    fee, distance = delivery.values()

    assert total_price == 1190
    assert total_price == cart_value + fee + small_order_surcharge
    assert small_order_surcharge == 0
    assert cart_value == 1000
    assert fee == 190
    assert distance == 224

    res = calculate_price(test_db[1], 500, [1000, 1000])
    total_price, small_order_surcharge, cart_value, delivery = res.values()
    fee, distance = delivery.values()

    assert total_price == 1390
    assert total_price == cart_value + fee + small_order_surcharge
    assert small_order_surcharge == 500
    assert cart_value == 500
    assert fee == 390
    assert distance == 1368
