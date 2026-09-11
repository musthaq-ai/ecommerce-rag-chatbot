import streamlit as st

from data.products import products
from utils.cart import (
    get_cart_count,
    remove_from_cart,
    update_quantity,
    clear_cart
)


st.set_page_config(
    page_title="Cart - ShopX",
    page_icon="🛒",
    layout="wide"
)


st.title("🛒 Shopping Cart")

if st.button("← Continue Shopping"):
    st.switch_page("pages/products.py")

# --------------------------------
# Initialize cart
# --------------------------------

if "cart" not in st.session_state:
    st.session_state.cart = {}


cart = st.session_state.cart


# --------------------------------
# Empty cart
# --------------------------------

if not cart:

    st.info("Your cart is empty.")

    if st.button("🛍️ Continue Shopping"):
        st.switch_page("pages/products.py")

    st.stop()


# --------------------------------
# Cart summary
# --------------------------------

st.write(
    f"**{get_cart_count()} item(s) in your cart**"
)

st.divider()


total = 0


# --------------------------------
# Cart items
# --------------------------------

for product_id, quantity in list(cart.items()):

    product = next(
        (
            item
            for item in products
            if item["id"] == product_id
        ),
        None
    )

    if product is None:
        continue


    item_total = product["price"] * quantity

    total += item_total


    image_col, details_col, quantity_col, total_col = st.columns(
        [1, 3, 1.5, 1.5]
    )


    with image_col:

        st.image(
            product["image"],
            width=120
        )


    with details_col:

        st.subheader(product["name"])

        st.caption(
            f"{product['brand']} • {product['category']}"
        )

        st.write(
            f"₹{product['price']:,} each"
        )


    with quantity_col:

        new_quantity = st.number_input(
            "Qty",
            min_value=0,
            max_value=product["stock"],
            value=quantity,
            key=f"quantity_{product_id}"
        )

        if new_quantity != quantity:

            update_quantity(
                product_id,
                new_quantity
            )

            st.rerun()


    with total_col:

        st.write("**Item Total**")

        st.write(
            f"### ₹{item_total:,}"
        )

        if st.button(
            "Remove",
            key=f"remove_{product_id}"
        ):

            remove_from_cart(product_id)

            st.rerun()


    st.divider()


# --------------------------------
# Order summary
# --------------------------------

st.subheader("Order Summary")


summary_col1, summary_col2 = st.columns(
    [3, 1]
)


with summary_col1:

    st.write("Subtotal")


with summary_col2:

    st.write(f"**₹{total:,}**")


st.write("Shipping")

st.write("**FREE**")


st.divider()


final_col1, final_col2 = st.columns(
    [3, 1]
)


with final_col1:

    st.subheader("Total")


with final_col2:

    st.subheader(f"₹{total:,}")


st.divider()


# --------------------------------
# Actions
# --------------------------------

button1, button2 = st.columns(2)


with button1:

    if st.button(
        "🛍️ Continue Shopping",
        use_container_width=True
    ):

        st.switch_page("pages/products.py")


with button2:

    if st.button(
        "🗑️ Clear Cart",
        use_container_width=True
    ):

        clear_cart()

        st.rerun()


st.success(
    "Checkout will be implemented in a later phase."
)