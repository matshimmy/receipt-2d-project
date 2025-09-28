import random
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from faker import Faker


class ProductDatabase:
    def __init__(self, seed: Optional[int] = None):
        if seed:
            random.seed(seed)
        self.fake = Faker()
        if seed:
            Faker.seed(seed)

        self.grocery_items = [
            {"name": "Milk 1 Gallon", "min_price": 3.99, "max_price": 5.99, "category": "Dairy"},
            {"name": "Eggs Dozen", "min_price": 2.99, "max_price": 4.99, "category": "Dairy"},
            {"name": "Bread Whole Wheat", "min_price": 2.49, "max_price": 3.99, "category": "Bakery"},
            {"name": "Chicken Breast", "min_price": 6.99, "max_price": 12.99, "category": "Meat"},
            {"name": "Ground Beef", "min_price": 5.99, "max_price": 9.99, "category": "Meat"},
            {"name": "Bananas", "min_price": 0.59, "max_price": 0.89, "category": "Produce"},
            {"name": "Apples", "min_price": 1.49, "max_price": 2.99, "category": "Produce"},
            {"name": "Tomatoes", "min_price": 2.99, "max_price": 4.99, "category": "Produce"},
            {"name": "Potatoes 5lb", "min_price": 3.99, "max_price": 5.99, "category": "Produce"},
            {"name": "Orange Juice", "min_price": 3.99, "max_price": 5.99, "category": "Beverages"},
            {"name": "Coffee", "min_price": 7.99, "max_price": 14.99, "category": "Beverages"},
            {"name": "Pasta", "min_price": 1.99, "max_price": 3.49, "category": "Pantry"},
            {"name": "Rice 2lb", "min_price": 4.99, "max_price": 7.99, "category": "Pantry"},
            {"name": "Cereal", "min_price": 3.99, "max_price": 5.99, "category": "Pantry"},
            {"name": "Yogurt", "min_price": 0.99, "max_price": 1.99, "category": "Dairy"},
            {"name": "Cheese", "min_price": 4.99, "max_price": 8.99, "category": "Dairy"},
            {"name": "Ice Cream", "min_price": 3.99, "max_price": 6.99, "category": "Frozen"},
            {"name": "Frozen Pizza", "min_price": 5.99, "max_price": 9.99, "category": "Frozen"},
            {"name": "Chips", "min_price": 2.99, "max_price": 4.99, "category": "Snacks"},
            {"name": "Cookies", "min_price": 3.49, "max_price": 5.49, "category": "Snacks"},
        ]

        self.restaurant_items = [
            {"name": "Caesar Salad", "min_price": 8.99, "max_price": 12.99, "category": "Starters"},
            {"name": "French Onion Soup", "min_price": 6.99, "max_price": 9.99, "category": "Starters"},
            {"name": "Chicken Wings", "min_price": 10.99, "max_price": 14.99, "category": "Starters"},
            {"name": "Grilled Salmon", "min_price": 18.99, "max_price": 26.99, "category": "Main"},
            {"name": "Ribeye Steak", "min_price": 24.99, "max_price": 34.99, "category": "Main"},
            {"name": "Chicken Parmesan", "min_price": 15.99, "max_price": 19.99, "category": "Main"},
            {"name": "Pasta Carbonara", "min_price": 14.99, "max_price": 18.99, "category": "Main"},
            {"name": "Burger & Fries", "min_price": 12.99, "max_price": 16.99, "category": "Main"},
            {"name": "Fish & Chips", "min_price": 13.99, "max_price": 17.99, "category": "Main"},
            {"name": "Vegetable Stir Fry", "min_price": 11.99, "max_price": 14.99, "category": "Main"},
            {"name": "Chocolate Cake", "min_price": 6.99, "max_price": 8.99, "category": "Dessert"},
            {"name": "Cheesecake", "min_price": 7.99, "max_price": 9.99, "category": "Dessert"},
            {"name": "Ice Cream Sundae", "min_price": 5.99, "max_price": 7.99, "category": "Dessert"},
            {"name": "Soft Drink", "min_price": 2.99, "max_price": 3.99, "category": "Beverages"},
            {"name": "Coffee", "min_price": 2.99, "max_price": 4.99, "category": "Beverages"},
            {"name": "Wine Glass", "min_price": 7.99, "max_price": 12.99, "category": "Beverages"},
            {"name": "Beer", "min_price": 4.99, "max_price": 6.99, "category": "Beverages"},
        ]

        self.retail_items = [
            {"name": "T-Shirt", "min_price": 14.99, "max_price": 29.99, "category": "Clothing"},
            {"name": "Jeans", "min_price": 39.99, "max_price": 79.99, "category": "Clothing"},
            {"name": "Sweater", "min_price": 29.99, "max_price": 59.99, "category": "Clothing"},
            {"name": "Dress", "min_price": 49.99, "max_price": 99.99, "category": "Clothing"},
            {"name": "Sneakers", "min_price": 59.99, "max_price": 129.99, "category": "Footwear"},
            {"name": "Boots", "min_price": 79.99, "max_price": 149.99, "category": "Footwear"},
            {"name": "Sandals", "min_price": 24.99, "max_price": 49.99, "category": "Footwear"},
            {"name": "Backpack", "min_price": 29.99, "max_price": 69.99, "category": "Accessories"},
            {"name": "Wallet", "min_price": 19.99, "max_price": 49.99, "category": "Accessories"},
            {"name": "Belt", "min_price": 24.99, "max_price": 44.99, "category": "Accessories"},
            {"name": "Watch", "min_price": 49.99, "max_price": 199.99, "category": "Accessories"},
            {"name": "Sunglasses", "min_price": 29.99, "max_price": 89.99, "category": "Accessories"},
            {"name": "Scarf", "min_price": 14.99, "max_price": 34.99, "category": "Accessories"},
            {"name": "Hat", "min_price": 19.99, "max_price": 39.99, "category": "Accessories"},
            {"name": "Jacket", "min_price": 69.99, "max_price": 149.99, "category": "Outerwear"},
            {"name": "Coat", "min_price": 99.99, "max_price": 249.99, "category": "Outerwear"},
        ]

        self.store_names = {
            "grocery": [
                "FreshMart", "SuperSave", "Green Grocer", "QuickStop Market",
                "Valley Foods", "City Market", "Food Palace", "MegaMart"
            ],
            "restaurant": [
                "The Golden Fork", "Bella Vista", "Harbor Grill", "The Cozy Kitchen",
                "Urban Eats", "Sunset Bistro", "The Garden Table", "Blue Moon Cafe"
            ],
            "retail": [
                "Fashion Forward", "Style House", "Trendy Threads", "Urban Outfitters",
                "The Clothing Co.", "Fashion Plaza", "Style Central", "Wardrobe World"
            ]
        }

    def get_random_products(self, store_type: str, count: int) -> List[Dict]:
        if store_type == "grocery":
            items = self.grocery_items
        elif store_type == "restaurant":
            items = self.restaurant_items
        elif store_type == "retail":
            items = self.retail_items
        else:
            items = self.grocery_items

        selected = random.sample(items, min(count, len(items)))
        products = []

        for item in selected:
            quantity = 1 if store_type == "restaurant" else random.randint(1, 3)
            unit_price = round(random.uniform(item["min_price"], item["max_price"]), 2)

            products.append({
                "name": item["name"],
                "category": item["category"],
                "quantity": quantity,
                "unit_price": unit_price,
                "total": round(quantity * unit_price, 2)
            })

        return products

    def get_random_store_info(self, store_type: str) -> Dict:
        store_name = random.choice(self.store_names.get(store_type, self.store_names["grocery"]))

        return {
            "name": store_name,
            "address": [
                self.fake.street_address(),
                f"{self.fake.city()}, {self.fake.state_abbr()} {self.fake.zipcode()}"
            ],
            "phone": self.fake.phone_number()
        }

    def generate_transaction_data(self, store_type: str = "grocery") -> Dict:
        store_info = self.get_random_store_info(store_type)

        # Generate 3-15 items
        num_items = random.randint(3, 15)
        items = self.get_random_products(store_type, num_items)

        subtotal = sum(item["total"] for item in items)
        tax_rate = random.uniform(0.05, 0.10)
        tax = round(subtotal * tax_rate, 2)
        total = round(subtotal + tax, 2)

        # Generate timestamp
        days_ago = random.randint(0, 30)
        transaction_time = datetime.now() - timedelta(days=days_ago)
        transaction_time = transaction_time.replace(
            hour=random.randint(8, 22),
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )

        # Generate transaction ID
        transaction_id = ''.join(random.choices('0123456789ABCDEF', k=12))

        return {
            "store": store_info,
            "items": items,
            "subtotal": subtotal,
            "tax": tax,
            "total": total,
            "transaction_id": transaction_id,
            "timestamp": transaction_time.strftime("%m/%d/%Y %I:%M:%S %p"),
            "payment_method": random.choice(["VISA", "MASTERCARD", "CASH", "DEBIT"])
        }