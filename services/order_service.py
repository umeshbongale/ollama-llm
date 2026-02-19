import re
from core.state import get_order, reset_order
from retrieval import get_all_categories, search_products_with_filters


# ==============================
# HELPERS
# ==============================

def extract_quantity(text: str) -> int:
    match = re.search(r"\b(\d+)\b", text)
    return int(match.group(1)) if match else 1


# ==============================
# PRODUCT RETRIEVAL
# ==============================

def retrieve_relevant_products(user_message: str):
    """
    Retrieve products based on category match.
    Fallback: return top cheapest products.
    """

    categories = get_all_categories()
    user_text = user_message.lower()

    # Category match
    for c in categories:
        if c.lower() in user_text:
            return search_products_with_filters(category=c)

    # Fallback → return cheapest products
    return search_products_with_filters()


# ==============================
# ORDER FLOW HANDLER
# ==============================

def handle_message(session_id: str, user_message: str):
    """
    Handles structured order flow:
    - Category detected → ask quantity
    - Quantity received → ask address
    - Address received → confirm order
    """

    order = get_order(session_id)
    user_text = user_message.lower()

    categories = get_all_categories()

    # ==============================
    # CATEGORY MATCH → START ORDER
    # ==============================
    for c in categories:
        if c.lower() in user_text:

            products = search_products_with_filters(category=c)

            if products:
                order["stage"] = "awaiting_quantity"
                order["product"] = {
                    "name": products[0][0],
                    "price": float(products[0][1]),
                    "features": products[0][2]
                }

                return f"""
### {products[0][0]}

💰 Price: ₹{products[0][1]}

How many quantity would you like?
"""

    # ==============================
    # GET QUANTITY
    # ==============================
    if order.get("stage") == "awaiting_quantity":
        qty = extract_quantity(user_text)
        order["quantity"] = qty
        order["stage"] = "awaiting_address"
        return "📦 Please provide delivery address."

    # ==============================
    # GET ADDRESS
    # ==============================
    if order.get("stage") == "awaiting_address":
        order["address"] = user_message

        product = order["product"]
        total = product["price"] * order["quantity"]

        reset_order(session_id)

        return f"""
## ✅ Order Confirmed

Product: {product['name']}
Price: ₹{product['price']}
Quantity: {order['quantity']}
Total: ₹{total}

Address:
{order['address']}
"""

    return None
