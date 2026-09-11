import streamlit as st

from data.products import products
from utils.cart import add_to_cart
from utils.auth import require_auth

require_auth()

st.set_page_config(
    page_title="Product Details - ShopX",
    page_icon="🛍️",
    layout="wide"
)


# --------------------------------
# Check selected product
# --------------------------------

if "selected_product_id" not in st.session_state:
    st.warning("No product selected.")

    if st.button("← Back to Products"):
        st.switch_page("pages/products.py")

    st.stop()


product_id = st.session_state.selected_product_id


# --------------------------------
# Find product
# --------------------------------

product = next(
    (
        item
        for item in products
        if item["id"] == product_id
    ),
    None
)


if product is None:
    st.error("Product not found.")
    st.stop()


# --------------------------------
# Back button
# --------------------------------

if st.button("← Back to Products"):
    st.switch_page("pages/products.py")


st.divider()


# --------------------------------
# Product information
# --------------------------------

image_column, details_column = st.columns(
    [1, 1]
)


with image_column:

    st.image(
        product["image"],
        use_container_width=True
    )


with details_column:

    st.title(product["name"])

    st.caption(
        f"{product['brand']} • {product['category']}"
    )

    st.write(
        f"⭐ {product['rating']} / 5"
    )

    st.markdown(
        f"# ₹{product['price']:,}"
    )

    st.write(product["description"])

    st.divider()

    st.subheader("Specifications")

    for key, value in product["specifications"].items():

        st.write(
            f"**{key}:** {value}"
        )

    st.divider()

    # Stock status

    if product["stock"] > 0:

        st.success(
            f"✓ In stock — {product['stock']} available"
        )

        quantity = st.number_input(
            "Quantity",
            min_value=1,
            max_value=product["stock"],
            value=1,
            step=1
        )

        if st.button(
            "🛒 Add to Cart",
            use_container_width=True
        ):

            add_to_cart(
                product["id"],
                quantity
            )

            st.success(
                f"{quantity} × {product['name']} "
                "added to your cart!"
            )

    else:

        st.error("Currently out of stock.")


# --------------------------------
# Product information
# --------------------------------

st.divider()

st.subheader("About this product")

st.write(product["description"])