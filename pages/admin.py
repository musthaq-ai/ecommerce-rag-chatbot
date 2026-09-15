import streamlit as st
import json

from utils.auth import require_admin
from utils.supabase_client import supabase


# ==========================================
# Admin Authentication
# ==========================================

require_admin()


# ==========================================
# Page Configuration
# ==========================================

st.set_page_config(
    page_title="Admin Dashboard - ShopX",
    page_icon="🛠️",
    layout="wide"
)


# ==========================================
# Header
# ==========================================

st.title("🛠️ Admin Dashboard")
st.write("Manage your ShopX store from here.")


# ==========================================
# Dashboard Tabs
# ==========================================

tab1, tab2, tab3 = st.tabs([
    "📦 Products",
    "📋 Orders",
    "📊 Overview"
])


# ==========================================
# TAB 1 — PRODUCTS
# ==========================================

with tab1:

    st.subheader("Product Management")

    # --------------------------------------
    # Add Product
    # --------------------------------------

    with st.expander(
        "➕ Add New Product",
        expanded=True
    ):

        name = st.text_input(
            "Product Name",
            key="admin_product_name"
        )

        brand = st.text_input(
            "Brand",
            key="admin_product_brand"
        )

        category = st.text_input(
            "Category",
            key="admin_product_category"
        )

        description = st.text_area(
            "Description",
            key="admin_product_description"
        )

        price = st.number_input(
            "Price (₹)",
            min_value=0.0,
            step=100.0,
            key="admin_product_price"
        )

        rating = st.number_input(
            "Rating",
            min_value=0.0,
            max_value=5.0,
            step=0.1,
            value=4.0,
            key="admin_product_rating"
        )

        stock = st.number_input(
            "Stock",
            min_value=0,
            step=1,
            key="admin_product_stock"
        )

        image_url = st.text_input(
            "Image URL",
            key="admin_product_image"
        )

        specifications = st.text_area(
            "Specifications (JSON)",
            value="{}",
            key="admin_product_specs"
        )

        if st.button(
            "Add Product",
            type="primary",
            key="add_product_btn"
        ):

            if not name.strip():

                st.error(
                    "Product name is required."
                )

            elif price <= 0:

                st.error(
                    "Product price must be greater than 0."
                )

            else:

                try:

                    import json

                    specs = json.loads(
                        specifications
                    )

                    product_data = {
                        "name": name,
                        "brand": brand,
                        "category": category,
                        "description": description,
                        "price": price,
                        "rating": rating,
                        "stock": stock,
                        "image_url": image_url,
                        "specifications": specs
                    }

                    (
                        supabase
                        .table("products")
                        .insert(product_data)
                        .execute()
                    )

                    st.success(
                        "✅ Product added successfully!"
                    )

                    st.rerun()

                except json.JSONDecodeError:

                    st.error(
                        "Specifications must be valid JSON."
                    )

                except Exception as e:

                    st.error(
                        f"Failed to add product: {e}"
                    )

    st.divider()

    # --------------------------------------
    # Existing Products
    # --------------------------------------

    st.subheader("Existing Products")

    try:

        response = (
            supabase
            .table("products")
            .select("*")
            .order("id")
            .execute()
        )

        db_products = response.data

        if not db_products:
            st.info("No products found.")
        else:
            for product in db_products:
                with st.expander(
                    f"{product['name']} — ₹{float(product['price']):,.2f}",
                    expanded=False
                ):
                    edit_col1, edit_col2 = st.columns([3, 1])

                    with edit_col1:
                        name = st.text_input(
                            "Product Name",
                            value=product["name"],
                            key=f"edit_name_{product['id']}"
                        )

                        brand = st.text_input(
                            "Brand",
                            value=product["brand"] or "",
                            key=f"edit_brand_{product['id']}"
                        )

                        category = st.text_input(
                            "Category",
                            value=product["category"] or "",
                            key=f"edit_category_{product['id']}"
                        )

                        description = st.text_area(
                            "Description",
                            value=product["description"] or "",
                            key=f"edit_description_{product['id']}"
                        )

                        price = st.number_input(
                            "Price (₹)",
                            min_value=0.0,
                            value=float(product["price"]),
                            step=100.0,
                            key=f"edit_price_{product['id']}"
                        )

                        rating = st.number_input(
                            "Rating",
                            min_value=0.0,
                            max_value=5.0,
                            value=float(product["rating"] or 0),
                            step=0.1,
                            key=f"edit_rating_{product['id']}"
                        )

                        stock = st.number_input(
                            "Stock",
                            min_value=0,
                            value=int(product["stock"] or 0),
                            step=1,
                            key=f"edit_stock_{product['id']}"
                        )

                        image_url = st.text_input(
                            "Image URL",
                            value=product["image_url"] or "",
                            key=f"edit_image_{product['id']}"
                        )

                        existing_specs = product.get("specifications") or {}
                        specifications = st.text_area(
                            "Specifications (JSON)",
                            value=json.dumps(existing_specs, indent=2),
                            key=f"edit_specs_{product['id']}"
                        )

                    with edit_col2:
                        if image_url:
                            st.image(image_url, width=180)

                    action_col1, action_col2 = st.columns(2)

                    with action_col1:
                        if st.button(
                            "💾 Save Changes",
                            key=f"save_product_{product['id']}",
                            type="primary"
                        ):
                            try:
                                specs = json.loads(specifications)

                                if not name.strip():
                                    st.error("Product name is required.")
                                elif price <= 0:
                                    st.error("Product price must be greater than 0.")
                                elif not isinstance(specs, dict):
                                    st.error("Specifications must be a JSON object.")
                                else:
                                    update_data = {
                                        "name": name.strip(),
                                        "brand": brand.strip(),
                                        "category": category.strip(),
                                        "description": description.strip(),
                                        "price": price,
                                        "rating": rating,
                                        "stock": stock,
                                        "image_url": image_url.strip(),
                                        "specifications": specs
                                    }

                                    (
                                        supabase
                                        .table("products")
                                        .update(update_data)
                                        .eq("id", product["id"])
                                        .execute()
                                    )

                                    st.success("✅ Product updated successfully!")
                                    st.rerun()

                            except json.JSONDecodeError:
                                st.error("Specifications must be valid JSON.")
                            except Exception as e:
                                st.error(f"Update failed: {e}")

                    with action_col2:
                        if st.button(
                            "🗑️ Delete Product",
                            key=f"delete_{product['id']}"
                        ):
                            try:
                                (
                                    supabase
                                    .table("products")
                                    .delete()
                                    .eq("id", product["id"])
                                    .execute()
                                )

                                st.success("Product deleted.")
                                st.rerun()

                            except Exception as e:
                                st.error(f"Delete failed: {e}")
    except Exception as e:

        st.error(
            f"Failed to load products: {e}"
        )


# ==========================================
# TAB 2 — ORDERS
# ==========================================

with tab2:

    st.subheader("📋 Customer Orders")

    # --------------------------------------
    # Get Orders
    # --------------------------------------

    response = (
        supabase
        .table("orders")
        .select("*")
        .order(
            "created_at",
            desc=True
        )
        .execute()
    )

    orders = response.data


    # --------------------------------------
    # No Orders
    # --------------------------------------

    if not orders:

        st.info(
            "No customer orders yet."
        )


    # --------------------------------------
    # Display Orders
    # --------------------------------------

    else:

        st.write(
            f"Total Orders: **{len(orders)}**"
        )

        st.divider()


        for order in orders:

            order_id = order["id"]
            status = order["status"]

            with st.expander(
                f"🧾 SHOPX-{order_id:06d} "
                f"• {status.upper()} "
                f"• ₹{float(order['total_amount']):,.0f}"
            ):

                # ==========================
                # Customer Information
                # ==========================

                col1, col2 = st.columns(2)


                with col1:

                    st.markdown(
                        "### 👤 Customer"
                    )

                    # Get customer profile
                    profile_response = (
                        supabase
                        .table("profiles")
                        .select("name, email")
                        .eq("id", order["user_id"])
                        .execute()
                    )

                    customer_name = "Unknown"
                    customer_email = "Not available"

                    if profile_response.data:
                        profile = profile_response.data[0]
                        customer_name = profile.get("name") or "Unknown"
                        customer_email = profile.get("email") or "Not available"

                    st.write(
                        f"**Name:** {customer_name}"
                    )

                    st.write(
                        f"**Email:** {customer_email}"
                    )

                    st.write(
                        f"**User ID:** `{order['user_id']}`"
                    )

                    st.write(
                        f"**Payment:** {order['payment_method']}"
                    )

                    st.write(
                        f"**Order Date:** {order['created_at']}"
                    )


                # ==========================
                # Delivery Information
                # ==========================

                with col2:

                    st.markdown(
                        "### 📍 Delivery"
                    )

                    st.write(
                        order["shipping_address"]
                    )

                    st.write(
                        f"{order['city']}, "
                        f"{order['state']} - "
                        f"{order['pincode']}"
                    )


                st.divider()


                # ==========================
                # Ordered Products
                # ==========================

                st.markdown(
                    "### 🛍️ Ordered Products"
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


                order_items = (
                    items_response.data
                )


                if order_items:

                    for item in order_items:

                        product_id = (
                            item["product_id"]
                        )

                        product_name = (
                            f"Product #{product_id}"
                        )


                        # Get product name

                        product_response = (
                            supabase
                            .table("products")
                            .select("name")
                            .eq(
                                "id",
                                product_id
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


                        col1, col2, col3 = (
                            st.columns([5, 2, 2])
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
                        "No order items found."
                    )


                st.divider()


                # ==========================
                # Update Order Status
                # ==========================

                st.markdown(
                    "### 🔄 Update Order Status"
                )


                status_options = [
                    "pending",
                    "confirmed",
                    "shipped",
                    "delivered",
                    "cancelled"
                ]


                if status in status_options:

                    current_index = (
                        status_options.index(status)
                    )

                else:

                    current_index = 0


                new_status = st.selectbox(
                    "Status",
                    status_options,
                    index=current_index,
                    key=f"status_{order_id}"
                )


                if st.button(
                    "💾 Update Status",
                    key=f"update_status_{order_id}",
                    type="primary"
                ):

                    (
                        supabase
                        .table("orders")
                        .update(
                            {
                                "status": new_status
                            }
                        )
                        .eq(
                            "id",
                            order_id
                        )
                        .execute()
                    )


                    st.success(
                        f"Order status updated to "
                        f"**{new_status}**."
                    )


                    st.rerun()
# ==========================================
# TAB 3 — OVERVIEW
# ==========================================

with tab3:

    st.subheader("📊 Store Overview")

    # --------------------------------------
    # Get Product Count
    # --------------------------------------

    product_response = (
        supabase
        .table("products")
        .select("id", count="exact")
        .execute()
    )

    product_count = product_response.count or 0


    # --------------------------------------
    # Get Order Count
    # --------------------------------------

    order_response = (
        supabase
        .table("orders")
        .select("id", count="exact")
        .execute()
    )

    order_count = order_response.count or 0


    # --------------------------------------
    # Display Metrics
    # --------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            "📦 Total Products",
            product_count
        )


    with col2:

        st.metric(
            "📋 Total Orders",
            order_count
        )
