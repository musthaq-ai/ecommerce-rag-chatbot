import streamlit as st

from data.products import products
from utils.cart import clear_cart


st.set_page_config(
    page_title="Checkout - ShopX",
    page_icon="💳",
    layout="wide"
)


# ==========================================
# Check cart
# ==========================================

if "cart" not in st.session_state:
    st.session_state.cart = {}


cart = st.session_state.cart


if not cart:
    st.warning("Your cart is empty.")

    if st.button("🛍️ Continue Shopping"):
        st.switch_page("pages/products.py")

    st.stop()


# ==========================================
# Page title
# ==========================================

st.title("💳 Checkout")

st.write("Complete your order details below.")

st.divider()


# ==========================================
# Customer information
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
        placeholder="you@example.com"
    )


phone = st.text_input(
    "Phone Number",
    placeholder="Enter your phone number"
)


# ==========================================
# Shipping address
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
# Calculate order total
# ==========================================

subtotal = 0


for product_id, quantity in cart.items():

    product = next(
        (
            item
            for item in products
            if item["id"] == product_id
        ),
        None
    )

    if product:

        subtotal += product["price"] * quantity


shipping = 0

total = subtotal + shipping


# ==========================================
# Order summary
# ==========================================

st.subheader("🧾 Order Summary")


for product_id, quantity in cart.items():

    product = next(
        (
            item
            for item in products
            if item["id"] == product_id
        ),
        None
    )

    if product:

        item_total = product["price"] * quantity

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
                f"₹{item_total:,}"
            )


st.divider()


col1, col2 = st.columns(
    [4, 1]
)

with col1:

    st.write("Subtotal")

with col2:

    st.write(f"₹{subtotal:,}")


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
        f"₹{total:,}"
    )


# ==========================================
# Place order
# ==========================================

st.divider()

if st.button(
    "✅ Place Order",
    use_container_width=True
):

    # Validate customer information

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


    # Create a simple order ID

    import random

    order_id = (
        "SHOPX-"
        + str(random.randint(100000, 999999))
    )


    # Store order information
    st.session_state.last_order = {
        "order_id": order_id,
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


    # Clear cart

    clear_cart()


    # Go to confirmation page

    st.switch_page(
        "pages/order_confirmation.py"
    )