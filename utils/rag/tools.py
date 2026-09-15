from utils.supabase_client import supabase


def search_products(query, limit=5):
    """
    Search products using important words from the user's question.
    """

    if not query or not query.strip():
        return []

    # Remove common question words
    stop_words = {
        "what", "is", "the", "price", "of",
        "how", "much", "cost", "for",
        "a", "an", "this", "that",
        "please", "tell", "me", "about",
        "product", "available", "availability",
        "stock", "in", "my", "do", "you"
    }

    words = query.lower().replace("?", "").split()

    keywords = [
        word for word in words
        if word not in stop_words and len(word) > 2
    ]

    if not keywords:
        return []

    # Search each meaningful keyword
    results = []

    for keyword in keywords:
        response = (
            supabase
            .table("products")
            .select("*")
            .or_(
                f"name.ilike.%{keyword}%,"
                f"brand.ilike.%{keyword}%,"
                f"category.ilike.%{keyword}%,"
                f"description.ilike.%{keyword}%"
            )
            .limit(limit)
            .execute()
        )

        if response.data:
            results.extend(response.data)

    # Remove duplicates
    unique_products = {}

    for product in results:
        unique_products[product["id"]] = product

    return list(unique_products.values())[:limit]

def get_user_order_history(user_id, limit=20):
    """
    Get the logged-in user's order history,
    including the products in each order.
    """

    if not user_id:
        return []

    # Get only this user's orders
    orders_response = (
        supabase
        .table("orders")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    orders = orders_response.data or []

    if not orders:
        return []

    order_history = []

    for order in orders:

        # Get items belonging to this order
        items_response = (
            supabase
            .table("order_items")
            .select("*")
            .eq("order_id", order["id"])
            .execute()
        )

        items = items_response.data or []

        products = []

        for item in items:

            product_response = (
                supabase
                .table("products")
                .select("id,name,brand,category,image_url")
                .eq("id", item["product_id"])
                .limit(1)
                .execute()
            )

            product = (
                product_response.data[0]
                if product_response.data
                else None
            )

            products.append({
                "product_id": item["product_id"],
                "product_name": product["name"] if product else "Unknown product",
                "brand": product.get("brand") if product else None,
                "quantity": item["quantity"],
                "price": item["price"]
            })

        order_history.append({
            "order_id": order["id"],
            "status": order["status"],
            "total_amount": order["total_amount"],
            "payment_method": order["payment_method"],
            "shipping_address": order["shipping_address"],
            "city": order["city"],
            "state": order["state"],
            "pincode": order["pincode"],
            "created_at": order["created_at"],
            "estimated_delivery_date": order["estimated_delivery_date"],
            "items": products
        })

    return order_history

def get_product_by_name(product_name):
    """
    Find a product using its name.
    """

    if not product_name or not product_name.strip():
        return None

    response = (
        supabase
        .table("products")
        .select("*")
        .ilike("name", f"%{product_name.strip()}%")
        .limit(1)
        .execute()
    )

    if response.data:
        return response.data[0]

    return None


def get_product_price(product_name):
    """
    Get the current price of a product.
    """

    product = get_product_by_name(product_name)

    if not product:
        return None

    return {
        "name": product["name"],
        "price": product["price"]
    }


def get_product_stock(product_name):
    """
    Get the current stock of a product.
    """

    product = get_product_by_name(product_name)

    if not product:
        return None

    return {
        "name": product["name"],
        "stock": product["stock"]
    }


def get_user_orders(user_id, limit=10):
    """
    Get orders belonging to the currently logged-in user.
    """

    if not user_id:
        return []

    response = (
        supabase
        .table("orders")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    return response.data or []


def get_order_by_id(order_id, user_id):
    """
    Get a specific order belonging to the current user.
    """

    if not order_id or not user_id:
        return None

    response = (
        supabase
        .table("orders")
        .select("*")
        .eq("id", order_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )

    if response.data:
        return response.data[0]

    return None


def get_order_status(order_id, user_id):
    """
    Get the current status and delivery information
    of a user's order.
    """

    order = get_order_by_id(order_id, user_id)

    if not order:
        return None

    return {
        "order_id": order["id"],
        "status": order["status"],
        "created_at": order["created_at"],
        "estimated_delivery_date": order.get(
            "estimated_delivery_date"
        )
    }