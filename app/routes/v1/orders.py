"""
This module defines the API routes for order management.
"""

from fastapi import APIRouter

router = APIRouter()

orders = [
    {
        "customer_name": "John Doe",
        "date": "2025-04-06",
        "order_id": 13,
        "order_status": "Shipped",
        "order": [
            {"product_id": 1, "product_name": "Pure Chocolate", "quantity": 2},
            {"product_id": 2, "product_name": "Hazelnut Chocolate", "quantity": 1},
        ],
        "total_price": 37.0,
        "transaction_status": "Completed",
    },
    {
        "customer_name": "Jane Smith",
        "date": "2025-04-28",
        "order_id": 42,
        "order_status": "Processing",
        "order": [
            {"product_id": 3, "product_name": "Pecan Nut Chocolate", "quantity": 3}
        ],
        "total_price": 60.0,
        "transaction_status": "Pending",
    },
    {
        "customer_name": "John Doe",
        "date": "2025-04-28",
        "order_id": 216,
        "order_status": "Delivered",
        "order": [
            {"product_id": 1, "product_name": "Pure Chocolate", "quantity": 1},
            {"product_id": 3, "product_name": "Pecan Nut Chocolate", "quantity": 2},
        ],
        "total_price": 51.0,
        "transaction_status": "Completed",
    },
]


@router.get("/")
def get_orders():
    """Retrieve all orders."""
    return orders
