import streamlit as st

from data.products import products
from utils.cart import (
    get_cart_count,
    remove_from_cart,
    update_quantity,
    clear_cart
)
from utils.auth import require_user, get_current_user_role
from utils.nav import render_sidebar


# --------------------------------
# Authentication
# --------------------------------

require_user()

st.set_page_config(
    page_title="Shopping Cart - ShopX",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

render_sidebar(get_current_user_role())


# --------------------------------
# Custom CSS
# --------------------------------

st.markdown(
    """
    <style>

    .cart-header {
        padding: 10px 0 24px 0;
    }

    .cart-title {
        font-size: 38px;
        font-weight: 750;
        margin-bottom: 4px;
    }

    .cart-subtitle {
        color: #6b7280;
        font-size: 16px;
    }

    .cart-card {
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 14px;
        background: white;
    }

    .product-name {
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .product-meta {
        color: #6b7280;
        font-size: 14px;
        margin-bottom: 12px;
    }

    .price {
        font-size: 18px;
        font-weight: 700;
    }

    .item-total {
        font-size: 21px;
        font-weight: 750;
    }

    .summary-card {
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 24px;
        background: white;
        position: sticky;
        top: 20px;
    }

    .summary-title {
        font-size: 24px;
        font-weight: 750;
        margin-bottom: 20px;
    }

    .summary-row {
        display: flex;
        justify-content: space-between;
        margin: 12px 0;
        color: #4b5563;
    }

    .summary-total {
        display: flex;
        justify-content: space-between;
        font-size: 24px;
        font-weight: 750;
        margin-top: 18px;
    }

    .free-shipping {
        color: #15803d;
        font-weight: 650;
    }

    .empty-cart {
        text-align: center;
        padding: 70px 20px;
        border: 1px dashed #d1d5db;
        border-radius: 18px;
        background: #fafafa;
    }

    .empty-cart-icon {
        font-size: 52px;
        margin-bottom: 12px;
    }

    .empty-cart-title {
        font-size: 28px;
        font-weight: 750;
    }

    .empty-cart-text {
        color: #6b7280;
        margin-bottom: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------
# Header
# --------------------------------

st.markdown(
    """
    <div class="cart-header">
        <div class="cart-title">🛒 Your Shopping Cart</div>
        <div class="cart-subtitle">
            Review your items before placing your order.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


if st.button("← Continue Shopping", key="top_continue"):
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

    st.markdown(
        """
        <div class="empty-cart">
            <div class="empty-cart-icon">🛒</div>
            <div class="empty-cart-title">Your cart is empty</div>
            <div class="empty-cart-text">
                Looks like you haven't added anything to your cart yet.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        if st.button(
            "🛍️ Start Shopping",
            use_container_width=True,
            type="primary"
        ):
            st.switch_page("pages/products.py")

    st.stop()


# --------------------------------
# Cart count
# --------------------------------

item_count = get_cart_count()

st.caption(
    f"{item_count} item{'s' if item_count != 1 else ''} in your cart"
)

st.write("")


# --------------------------------
# Main layout
# --------------------------------

items_column, summary_column = st.columns(
    [2.1, 1],
    gap="large"
)


total = 0


# --------------------------------
# Cart Items
# --------------------------------

with items_column:

    st.subheader("Cart Items")

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

        # Product card
        st.markdown(
            '<div class="cart-card">',
            unsafe_allow_html=True
        )

        image_col, details_col, quantity_col, total_col = st.columns(
            [1.1, 3.2, 1.5, 1.5],
            vertical_alignment="center"
        )

        # --------------------------------
        # Image
        # --------------------------------

        with image_col:

            st.image(
                product["image"],
                use_container_width=True
            )

        # --------------------------------
        # Product details
        # --------------------------------

        with details_col:

            st.markdown(
                f"""
                <div class="product-name">
                    {product['name']}
                </div>

                <div class="product-meta">
                    {product['brand']} • {product['category']}
                </div>

                <div class="price">
                    ₹{product['price']:,}
                </div>
                """,
                unsafe_allow_html=True
            )

            if product["stock"] > 0:

                st.caption(
                    f"✓ {product['stock']} available"
                )

            else:

                st.error("Out of stock")

        # --------------------------------
        # Quantity
        # --------------------------------

        with quantity_col:

            new_quantity = st.number_input(
                "Quantity",
                min_value=0,
                max_value=max(product["stock"], quantity),
                value=quantity,
                step=1,
                key=f"quantity_{product_id}"
            )

            if new_quantity != quantity:

                update_quantity(
                    product_id,
                    new_quantity
                )

                st.rerun()

        # --------------------------------
        # Item total
        # --------------------------------

        with total_col:

            st.caption("Item Total")

            st.markdown(
                f"""
                <div class="item-total">
                    ₹{item_total:,}
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button(
                "Remove",
                key=f"remove_{product_id}",
                use_container_width=True
            ):

                remove_from_cart(product_id)

                st.rerun()

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


# --------------------------------
# Order Summary
# --------------------------------

with summary_column:

    st.markdown(
        """
        <div class="summary-card">
            <div class="summary-title">
                Order Summary
            </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="summary-row">
            <span>Items</span>
            <strong>{item_count}</strong>
        </div>

        <div class="summary-row">
            <span>Subtotal</span>
            <strong>₹{total:,}</strong>
        </div>

        <div class="summary-row">
            <span>Shipping</span>
            <strong class="free-shipping">FREE</strong>
        </div>

        <hr>

        <div class="summary-total">
            <span>Total</span>
            <span>₹{total:,}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    if st.button(
        "💳 Proceed to Checkout",
        use_container_width=True,
        type="primary"
    ):
        st.switch_page("pages/checkout.py")

    st.write("")

    if st.button(
        "🛍️ Continue Shopping",
        use_container_width=True
    ):
        st.switch_page("pages/products.py")

    st.write("")

    if st.button(
        "🗑️ Clear Cart",
        use_container_width=True
    ):
        clear_cart()
        st.rerun()

    st.markdown(
        """
        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------
# Bottom information
# --------------------------------

st.write("")
st.divider()

info1, info2, info3 = st.columns(3)

with info1:
    st.markdown("### 🚚 Fast Delivery")
    st.caption("Get your products delivered quickly.")

with info2:
    st.markdown("### 🔒 Secure Checkout")
    st.caption("Your order information is protected.")

with info3:
    st.markdown("### ↩️ Easy Shopping")
    st.caption("Review your cart before placing the order.")