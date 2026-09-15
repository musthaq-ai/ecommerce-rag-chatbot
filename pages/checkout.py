import streamlit as st

from utils.cart import clear_cart
from utils.auth import require_auth
from utils.supabase_client import supabase
from datetime import date, timedelta

# ==========================================
# Authentication
# ==========================================

require_auth()


# ==========================================
# Page Configuration
# ==========================================

st.set_page_config(
    page_title="Checkout - ShopX",
    page_icon="💳",
    layout="wide"
)


# ==========================================
# Check Cart
# ==========================================

if "cart" not in st.session_state:
    st.session_state.cart = {}


cart = st.session_state.cart


if not cart:

    st.warning("Your cart is empty.")

    if st.button(
        "🛍️ Continue Shopping",
        key="continue_shopping_btn"
    ):
        st.switch_page("pages/products.py")

    st.stop()


# ==========================================
# Get Current User
# ==========================================

user = st.session_state.user


# ==========================================
# Fetch Products from Supabase
# ==========================================

try:

    response = (
        supabase
        .table("products")
        .select("*")
        .execute()
    )

    products = response.data

except Exception as e:

    st.error(
        f"Unable to load products: {e}"
    )

    st.stop()


# ==========================================
# Convert Products into Lookup Dictionary
# ==========================================

product_lookup = {
    product["id"]: product
    for product in products
}


# ==========================================
# Page Title
# ==========================================

st.title("💳 Checkout")

st.write(
    "Complete your order details below."
)

st.divider()


# ==========================================
# Customer Information
# ==========================================

st.subheader("👤 Customer Information")

col1, col2 = st.columns(2)


with col1:

    name = st.text_input(
        "Full Name",
        placeholder="Enter your full name"
    )


with col2:

    email = st.text_input(
        "Email Address",
        value=user.email or "",
        placeholder="you@example.com"
    )


phone = st.text_input(
    "Phone Number",
    placeholder="Enter your phone number"
)


# ==========================================
# Shipping Address
# ==========================================

st.subheader("📍 Shipping Address")

address = st.text_area(
    "Address",
    placeholder="House number, street, area..."
)


col1, col2, col3 = st.columns(3)


with col1:

    city = st.text_input(
        "City"
    )


with col2:

    state = st.text_input(
        "State"
    )


with col3:

    pincode = st.text_input(
        "PIN Code"
    )


# ==========================================
# Payment
# ==========================================

st.subheader("💳 Payment Method")

payment_method = st.radio(
    "Select payment method",
    [
        "Cash on Delivery",
        "UPI",
        "Credit / Debit Card"
    ]
)


st.divider()


# ==========================================
# Calculate Order
# ==========================================

subtotal = 0

valid_cart_items = []


for product_id, quantity in cart.items():

    product = product_lookup.get(product_id)

    if product:

        item_total = (
            float(product["price"]) * quantity
        )

        subtotal += item_total

        valid_cart_items.append(
            {
                "product": product,
                "quantity": quantity,
                "item_total": item_total
            }
        )


if not valid_cart_items:

    st.error(
        "The products in your cart are no longer available."
    )

    st.stop()


shipping = 0

total = subtotal + shipping


# ==========================================
# Order Summary
# ==========================================

st.subheader("🧾 Order Summary")


for item in valid_cart_items:

    product = item["product"]
    quantity = item["quantity"]
    item_total = item["item_total"]

    col1, col2, col3 = st.columns(
        [4, 1, 2]
    )

    with col1:

        st.write(
            f"**{product['name']}**"
        )

    with col2:

        st.write(
            f"× {quantity}"
        )

    with col3:

        st.write(
            f"₹{item_total:,.0f}"
        )


st.divider()


col1, col2 = st.columns(
    [4, 1]
)

with col1:

    st.write("Subtotal")


with col2:

    st.write(
        f"₹{subtotal:,.0f}"
    )


col1, col2 = st.columns(
    [4, 1]
)

with col1:

    st.write("Shipping")


with col2:

    st.write("FREE")


st.divider()


col1, col2 = st.columns(
    [4, 1]
)

with col1:

    st.subheader("Total")


with col2:

    st.subheader(
        f"₹{total:,.0f}"
    )


# ==========================================
# Place Order
# ==========================================

st.divider()


if st.button(
    "✅ Place Order",
    use_container_width=True,
    type="primary",
    key="place_order_btn"
):

    # --------------------------------------
    # Validate Customer Information
    # --------------------------------------

    if not name.strip():

        st.error(
            "Please enter your name."
        )

        st.stop()


    if not email.strip():

        st.error(
            "Please enter your email."
        )

        st.stop()


    if not phone.strip():

        st.error(
            "Please enter your phone number."
        )

        st.stop()


    if not address.strip():

        st.error(
            "Please enter your address."
        )

        st.stop()


    if not city.strip():

        st.error(
            "Please enter your city."
        )

        st.stop()


    if not state.strip():

        st.error(
            "Please enter your state."
        )

        st.stop()


    if not pincode.strip():

        st.error(
            "Please enter your PIN code."
        )

        st.stop()


    # --------------------------------------
    # Check Stock
    # --------------------------------------

    for item in valid_cart_items:

        product = item["product"]
        quantity = item["quantity"]

        if quantity > product["stock"]:

            st.error(
                f"Only {product['stock']} unit(s) "
                f"of {product['name']} are available."
            )

            st.stop()


    # --------------------------------------
    # Create Order
    # --------------------------------------

    try:

        estimated_delivery_date = (
    date.today() + timedelta(days=5)
)

        order_data = {
    "user_id": user.id,
    "total_amount": total,
    "status": "pending",
    "payment_method": payment_method,
    "shipping_address": address,
    "city": city,
    "state": state,
    "pincode": pincode,
    "estimated_delivery_date": estimated_delivery_date.isoformat()
}

        order_response = (
            supabase
    .table("orders")
    .insert(order_data)
    .select()
    .execute()
)

        if not order_response.data:
            raise Exception("Order was created but no order data was returned.")

        order = order_response.data[0]

        database_order_id = order["id"]


        # ----------------------------------
        # Create Order Items
        # ----------------------------------

        order_items = []


        for item in valid_cart_items:

            product = item["product"]
            quantity = item["quantity"]

            order_items.append(
                {
                    "order_id": database_order_id,
                    "product_id": product["id"],
                    "quantity": quantity,
                    "price": product["price"]
                }
            )


        supabase.table(
            "order_items"
        ).insert(
            order_items
        ).execute()


        # ----------------------------------
        # Create ShopX Order ID
        # ----------------------------------

        display_order_id = (
            f"SHOPX-{database_order_id:06d}"
        )


        # ----------------------------------
        # Save Order for Confirmation Page
        # ----------------------------------

        st.session_state.last_order = {

            "order_id": display_order_id,

            "database_order_id": database_order_id,

            "name": name,

            "email": email,

            "phone": phone,

            "address": address,

            "city": city,

            "state": state,

            "pincode": pincode,

            "payment_method": payment_method,

            "total": total

        }


        # ----------------------------------
        # Clear Cart
        # ----------------------------------

        clear_cart()


        # ----------------------------------
        # Go to Confirmation
        # ----------------------------------

        st.switch_page(
            "pages/order_confirmation.py"
        )


    except Exception as e:

        st.error(
            f"❌ Failed to place order: {e}"
        )