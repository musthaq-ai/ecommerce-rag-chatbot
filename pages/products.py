import streamlit as st

from utils.auth import require_user, get_current_user_role
from utils.nav import render_sidebar
from utils.supabase_client import supabase


# ==========================================
# Authentication (customer-only)
# ==========================================

require_user()

render_sidebar(get_current_user_role())


# ==========================================
# Page Configuration
# ==========================================

st.title("🛍️ ShopX Products")

st.write("Browse our products and find what you need.")


# ==========================================
# Fetch Products from Supabase
# ==========================================

try:

    response = (
        supabase
        .table("products")
        .select("*")
        .order("id")
        .execute()
    )

    products = response.data

except Exception as e:

    st.error(
        f"Unable to load products: {e}"
    )

    st.stop()


# ==========================================
# Check Products
# ==========================================

if not products:

    st.info(
        "No products are available right now."
    )

    st.stop()


# ==========================================
# Search
# ==========================================

search = st.text_input(
    "🔍 Search products",
    placeholder="Search by product name, brand or description..."
)


# ==========================================
# Category Filter
# ==========================================

categories = sorted(
    list(
        set(
            product["category"]
            for product in products
            if product.get("category")
        )
    )
)

selected_category = st.selectbox(
    "🏷️ Category",
    ["All"] + categories
)


# ==========================================
# Filter Products
# ==========================================

filtered_products = products


if search:

    search_lower = search.lower()

    filtered_products = [
        product
        for product in filtered_products
        if (
            search_lower in product.get("name", "").lower()
            or search_lower in product.get("brand", "").lower()
            or search_lower in product.get("description", "").lower()
        )
    ]


if selected_category != "All":

    filtered_products = [
        product
        for product in filtered_products
        if product.get("category") == selected_category
    ]


# ==========================================
# Results
# ==========================================

st.write(
    f"Showing **{len(filtered_products)}** product(s)"
)


if not filtered_products:

    st.warning(
        "No products match your search."
    )

    st.stop()


# ==========================================
# Product Cards
# ==========================================

columns = st.columns(3)


for index, product in enumerate(filtered_products):

    with columns[index % 3]:

        # ----------------------------------
        # Image
        # ----------------------------------

        if product.get("image_url"):

            st.image(
                product["image_url"],
                use_container_width=True
            )

        # ----------------------------------
        # Product information
        # ----------------------------------

        st.subheader(
            product["name"]
        )

        st.caption(
            f"{product.get('brand', '')} • "
            f"{product.get('category', '')}"
        )

        st.write(
            f"⭐ {product.get('rating', 0)} / 5"
        )

        st.markdown(
            f"### ₹{product['price']:,.0f}"
        )

        # ----------------------------------
        # Stock
        # ----------------------------------

        stock = product.get("stock", 0)

        if stock > 0:

            st.caption(
                f"📦 {stock} in stock"
            )

        else:

            st.error(
                "Out of stock"
            )

        # ----------------------------------
        # View Product
        # ----------------------------------

        if st.button(
            "View Product",
            key=f"view_product_{product['id']}",
            use_container_width=True
        ):

            st.session_state[
                "selected_product_id"
            ] = product["id"]

            st.switch_page(
                "pages/product_details.py"
            )