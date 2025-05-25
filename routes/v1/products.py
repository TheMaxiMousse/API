from fastapi import APIRouter

router = APIRouter()

products = [
    {
        "product_id": 1,
        "product_name": "Pure Chocolate",
        "price": 11.0,
        "status": "Available",
    },
    {
        "product_id": 2,
        "product_name": "Hazelnut Chocolate",
        "price": 15.0,
        "status": "Available",
    },
    {
        "product_id": 3,
        "product_name": "Pecan Nut Chocolate",
        "price": 20.0,
        "status": "Available",
    },
    {
        "product_id": 4,
        "product_name": "Almond Chocolate",
        "price": 12.0,
        "status": "Available",
    },
    {
        "product_id": 5,
        "product_name": "Macadamia Chocolate",
        "price": 18.0,
        "status": "Draft",
    },
    {
        "product_id": 6,
        "product_name": "Cashew Chocolate",
        "price": 14.0,
        "status": "Available",
    },
    {
        "product_id": 7,
        "product_name": "Pistachio Chocolate",
        "price": 22.0,
        "status": "Available",
    },
    {
        "product_id": 8,
        "product_name": "Walnut Chocolate",
        "price": 16.0,
        "status": "Discontinued",
    },
    {
        "product_id": 9,
        "product_name": "Coconut Chocolate",
        "price": 19.0,
        "status": "Available",
    },
]


@router.get("/")
def get_products():
    return products
