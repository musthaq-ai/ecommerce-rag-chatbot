import streamlit as st
from data.products import products


st.set_page_config(
    page_title="Products - ShopX",
    page_icon="🛍️",
    layout="wide"
)


st.title("🛍️ Product Catalog")

if st.button("← Home"):
    st.switch_page("app.py")

st.write("Explore our collection of products.")


# -------------------------
# Search and filter
# -------------------------

col1, col2 = st.columns([3, 1])

with col1:
    search = st.text_input(
        "🔎 Search products",
        placeholder="Search by product name or brand..."
    )

with col2:
    categories = ["All"] + sorted(
        list(set(product["category"] for product in products))
    )

    selected_category = st.selectbox(
        "Category",
        categories
    )


# -------------------------
# Filter products
# -------------------------

filtered_products = products

if search:
    search_lower = search.lower()

    filtered_products = [
        product
        for product in filtered_products
        if search_lower in product["name"].lower()
        or search_lower in product["brand"].lower()
        or search_lower in product["description"].lower()
    ]


if selected_category != "All":
    filtered_products = [
        product
        for product in filtered_products
        if product["category"] == selected_category
    ]


st.divider()

st.write(f"**{len(filtered_products)} products found**")


# -------------------------
# Product cards
# -------------------------

columns = st.columns(3)

for index, product in enumerate(filtered_products):

    with columns[index % 3]:

        st.image(
            product["image"],
            use_container_width=True
        )

        st.subheader(product["name"])

        st.caption(
            f"{product['brand']} • {product['category']}"
        )

        st.write(
            f"⭐ {product['rating']} / 5"
        )

        st.markdown(
            f"### ₹{product['price']:,}"
        )

        if product["stock"] > 0:
            st.success(
                f"✓ In stock ({product['stock']})"
            )
        else:
            st.error("Out of stock")

        if st.button(
            "View Details",
            key=f"view_{product['id']}"
        ):
            st.session_state["selected_product_id"] = product["id"]
            st.switch_page("pages/product_details.py")

        st.write("")