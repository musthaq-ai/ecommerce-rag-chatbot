import streamlit as st

from utils.auth import require_user, get_current_user_role
from utils.nav import render_sidebar
from utils.supabase_client import supabase


# ==========================================
# Authentication (customer-only)
# ==========================================

require_user()


# ==========================================
# Page Configuration
# ==========================================

st.set_page_config(
    page_title="My Orders - ShopX",
    page_icon="📋",
    layout="wide"
)

render_sidebar(get_current_user_role())


# ==========================================
# Current User
# ==========================================

user = st.session_state.user


# ==========================================
# Page Header
# ==========================================

st.title("📋 My Orders")

st.write(
    "View your previous orders and track their status."
)

st.divider()


# ==========================================
# Fetch User Orders
# ==========================================

response = (
    supabase
    .table("orders")
    .select("*")
    .eq("user_id", user.id)
    .order(
        "created_at",
        desc=True
    )
    .execute()
)

orders = response.data


# ==========================================
# No Orders
# ==========================================

if not orders:

    st.info(
        "You haven't placed any orders yet."
    )

    if st.button(
        "🛍️ Start Shopping",
        key="orders_shop_btn"
    ):

        st.switch_page(
            "pages/products.py"
        )

    st.stop()


# ==========================================
# Order Count
# ==========================================

st.write(
    f"You have placed **{len(orders)} order(s)**."
)


# ==========================================
# Display Orders
# ==========================================

for order in orders:

    order_id = order["id"]

    status = order["status"]

    total = float(
        order["total_amount"]
    )


    # --------------------------------------
    # Status Display
    # --------------------------------------

    status_icons = {
        "pending": "🟡",
        "confirmed": "🔵",
        "shipped": "🚚",
        "delivered": "🟢",
        "cancelled": "🔴"
    }

    status_icon = status_icons.get(
        status,
        "⚪"
    )


    # --------------------------------------
    # Order Card
    # --------------------------------------

    with st.container(border=True):

        col1, col2, col3 = st.columns(
            [4, 2, 2]
        )


        with col1:

            st.markdown(
                f"### 🧾 SHOPX-{order_id:06d}"
            )

            st.caption(
                f"Order Date: {order['created_at']}"
            )


        with col2:

            st.markdown(
                f"**{status_icon} "
                f"{status.upper()}**"
            )


        with col3:

            st.markdown(
                f"### ₹{total:,.0f}"
            )


        st.divider()


        # ----------------------------------
        # Delivery Information
        # ----------------------------------

        st.markdown(
            "### 📍 Delivery Address"
        )

        st.write(
            f"{order['shipping_address']}, "
            f"{order['city']}, "
            f"{order['state']} - "
            f"{order['pincode']}"
        )


        st.write(
            f"💳 Payment: "
            f"{order['payment_method']}"
        )


        st.divider()


        # ----------------------------------
        # Order Items
        # ----------------------------------

        st.markdown(
            "### 🛍️ Items"
        )


        items_response = (
            supabase
            .table("order_items")
            .select("*")
            .eq(
                "order_id",
                order_id
            )
            .execute()
        )

        order_items = items_response.data


        if order_items:

            for item in order_items:

                product_name = (
                    f"Product #{item['product_id']}"
                )


                product_response = (
                    supabase
                    .table("products")
                    .select("name")
                    .eq(
                        "id",
                        item["product_id"]
                    )
                    .execute()
                )


                if product_response.data:

                    product_name = (
                        product_response
                        .data[0]["name"]
                    )


                item_total = (
                    float(item["price"])
                    * item["quantity"]
                )


                col1, col2, col3 = st.columns(
                    [5, 2, 2]
                )


                with col1:

                    st.write(
                        product_name
                    )


                with col2:

                    st.write(
                        f"× {item['quantity']}"
                    )


                with col3:

                    st.write(
                        f"₹{item_total:,.0f}"
                    )


        else:

            st.info(
                "No items found for this order."
            )


        # ----------------------------------
        # Order Status Progress
        # ----------------------------------

        if status != "cancelled":

            st.divider()

            st.markdown(
                "### 🚚 Order Status"
            )

            status_steps = [
                "pending",
                "confirmed",
                "shipped",
                "delivered"
            ]

            current_index = status_steps.index(
                status
            ) if status in status_steps else 0


            progress = (
                current_index
                / (len(status_steps) - 1)
            )


            st.progress(
                progress
            )


            status_labels = [
                "🟡 Pending",
                "🔵 Confirmed",
                "🚚 Shipped",
                "🟢 Delivered"
            ]


            cols = st.columns(4)


            for index, label in enumerate(
                status_labels
            ):

                with cols[index]:

                    if index <= current_index:

                        st.success(
                            label
                        )

                    else:

                        st.caption(
                            label
                        )


        else:

            st.divider()

            st.error(
                "🔴 This order has been cancelled."
            )