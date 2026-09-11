import streamlit as st


st.set_page_config(
    page_title="Order Confirmed - ShopX",
    page_icon="✅",
    layout="wide"
)


# ==========================================
# Check order
# ==========================================

if "last_order" not in st.session_state:

    st.warning(
        "No recent order found."
    )

    if st.button("🛍️ Start Shopping"):

        st.switch_page(
            "pages/products.py"
        )

    st.stop()


order = st.session_state.last_order


# ==========================================
# Success message
# ==========================================

st.title("✅ Order Confirmed!")

st.success(
    "Thank you for shopping with ShopX!"
)


st.markdown(
    f"""
    ### Your order has been successfully placed.

    **Order ID:** `{order["order_id"]}`

    **Total Amount:** ₹{order["total"]:,}

    **Payment Method:** {order["payment_method"]}
    """
)


st.divider()


# ==========================================
# Delivery information
# ==========================================

st.subheader("📦 Delivery Information")

st.write(
    f"**Name:** {order['name']}"
)

st.write(
    f"**Email:** {order['email']}"
)

st.write(
    f"**Phone:** {order['phone']}"
)

st.write(
    f"**Address:** {order['address']}"
)

st.write(
    f"{order['city']}, "
    f"{order['state']} - "
    f"{order['pincode']}"
)


st.divider()


st.info(
    "Your order will be processed shortly. "
    "Order tracking will be available in a future version."
)


# ==========================================
# Navigation
# ==========================================

col1, col2 = st.columns(2)


with col1:

    if st.button(
        "🛍️ Continue Shopping",
        use_container_width=True
    ):

        st.switch_page(
            "pages/products.py"
        )


with col2:

    if st.button(
        "🏠 Go Home",
        use_container_width=True
    ):

        st.switch_page(
            "app.py"
        )