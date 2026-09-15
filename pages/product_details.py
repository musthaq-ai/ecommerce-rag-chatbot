import streamlit as st

from utils.cart import add_to_cart
from utils.auth import require_user, get_current_user_role
from utils.nav import render_sidebar
from utils.supabase_client import supabase


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Product Details - ShopX",
    page_icon="🛍️",
    layout="wide",
)


# =========================================================
# AUTHENTICATION
# =========================================================

require_user()

render_sidebar(get_current_user_role())


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       PAGE
       ===================================================== */

    .product-page-title {
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.8px;
        margin-bottom: 0.3rem;
    }

    .product-meta {
        color: #6b7280;
        font-size: 1rem;
        margin-bottom: 1rem;
    }


    /* =====================================================
       PRICE
       ===================================================== */

    .product-price {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 1rem 0;
    }


    /* =====================================================
       PRODUCT DESCRIPTION
       ===================================================== */

    .product-description {
        color: #4b5563;
        font-size: 1rem;
        line-height: 1.7;
    }


    /* =====================================================
       SPECIFICATIONS
       ===================================================== */

    .spec-title {
        font-size: 1.25rem;
        font-weight: 750;
        margin-bottom: 0.8rem;
    }

    .spec-row {
        padding: 0.7rem 0;
        border-bottom: 1px solid #e5e7eb;
    }


    /* =====================================================
       PRODUCT IMAGE
       ===================================================== */

    .image-placeholder {
        height: 500px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #f8fafc;
        border-radius: 20px;
        font-size: 5rem;
        border: 1px solid #e5e7eb;
    }


    /* =====================================================
       INFO CARDS
       ===================================================== */

    .info-card {
        padding: 1.2rem;
        border-radius: 16px;
        background: #f8fafc;
        border: 1px solid #e5e7eb;
        margin-top: 1rem;
    }

    .info-card-title {
        font-weight: 700;
        margin-bottom: 0.25rem;
    }

    .info-card-text {
        color: #6b7280;
        font-size: 0.9rem;
    }


    /* =====================================================
       STOCK
       ===================================================== */

    .stock-good {
        color: #047857;
        font-weight: 700;
    }

    .stock-low {
        color: #c2410c;
        font-weight: 700;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SELECTED PRODUCT CHECK
# =========================================================

if "selected_product_id" not in st.session_state:

    st.warning(
        "No product selected."
    )

    if st.button(
        "← Back to Products",
        use_container_width=True,
    ):

        st.switch_page(
            "pages/products.py"
        )

    st.stop()


product_id = st.session_state[
    "selected_product_id"
]


# =========================================================
# FETCH PRODUCT FROM SUPABASE
# =========================================================

try:

    response = (
        supabase
        .table("products")
        .select("*")
        .eq("id", product_id)
        .limit(1)
        .execute()
    )

    product_data = response.data or []

except Exception as e:

    st.error(
        f"Unable to load product: {e}"
    )

    st.stop()


# =========================================================
# PRODUCT NOT FOUND
# =========================================================

if not product_data:

    st.error(
        "Product not found."
    )

    if st.button(
        "← Back to Products",
        use_container_width=False,
    ):

        st.switch_page(
            "pages/products.py"
        )

    st.stop()


product = product_data[0]


# =========================================================
# BACK BUTTON
# =========================================================

if st.button(
    "← Back to Products",
    key="back_products_btn",
):

    st.switch_page(
        "pages/products.py"
    )


st.divider()


# =========================================================
# PRODUCT LAYOUT
# =========================================================

image_column, details_column = st.columns(
    [1.05, 1]
)


# =========================================================
# IMAGE
# =========================================================

with image_column:

    if product.get("image_url"):

        st.image(
            product["image_url"],
            use_container_width=True,
        )

    else:

        st.markdown(
            """
            <div class="image-placeholder">
                🛍️
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# PRODUCT DETAILS
# =========================================================

with details_column:

    st.markdown(
        f"""
        <div class="product-page-title">
            {product.get("name", "Product")}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="product-meta">
            {product.get("brand", "Unknown Brand")}
            &nbsp; • &nbsp;
            {product.get("category", "Uncategorized")}
        </div>
        """,
        unsafe_allow_html=True,
    )


    # -----------------------------------------------------
    # Rating
    # -----------------------------------------------------

    rating = float(
        product.get("rating", 0) or 0
    )

    st.write(
        f"⭐ {rating:.1f} / 5"
    )


    # -----------------------------------------------------
    # Price
    # -----------------------------------------------------

    price = float(
        product.get("price", 0) or 0
    )

    st.markdown(
        f"""
        <div class="product-price">
            ₹{price:,.0f}
        </div>
        """,
        unsafe_allow_html=True,
    )


    # -----------------------------------------------------
    # Description
    # -----------------------------------------------------

    description = product.get(
        "description",
        ""
    )

    st.markdown(
        f"""
        <div class="product-description">
            {description}
        </div>
        """,
        unsafe_allow_html=True,
    )


    st.divider()


    # =====================================================
    # STOCK / PURCHASE
    # =====================================================

    stock = int(
        product.get("stock", 0) or 0
    )


    if stock > 0:

        if stock <= 5:

            st.markdown(
                f"""
                <div class="stock-low">
                    ⚠️ Only {stock} left in stock
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.markdown(
                f"""
                <div class="stock-good">
                    ✓ In stock — {stock} available
                </div>
                """,
                unsafe_allow_html=True,
            )


        st.write("")


        quantity = st.number_input(
            "Quantity",
            min_value=1,
            max_value=stock,
            value=1,
            step=1,
            key="product_quantity",
        )


        if st.button(
            "🛒 Add to Cart",
            type="primary",
            use_container_width=True,
            key="add_to_cart_btn",
        ):

            add_to_cart(
                product["id"],
                quantity,
            )

            st.success(
                f"✓ {quantity} × "
                f"{product['name']} "
                f"added to your cart!"
            )


        if st.button(
            "🛒 View Cart",
            use_container_width=True,
            key="view_cart_btn",
        ):

            st.switch_page(
                "pages/cart.py"
            )


    else:

        st.error(
            "❌ This product is currently out of stock."
        )


# =========================================================
# PRODUCT BENEFITS
# =========================================================

st.divider()

benefit1, benefit2, benefit3 = st.columns(3)


with benefit1:

    st.markdown(
        """
        <div class="info-card">

            <div class="info-card-title">
                🚚 Fast Delivery
            </div>

            <div class="info-card-text">
                Quick and reliable delivery to
                your registered address.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with benefit2:

    st.markdown(
        """
        <div class="info-card">

            <div class="info-card-title">
                🔒 Secure Shopping
            </div>

            <div class="info-card-text">
                Your account and order information
                are protected.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with benefit3:

    st.markdown(
        """
        <div class="info-card">

            <div class="info-card-title">
                🤖 AI Assistance
            </div>

            <div class="info-card-text">
                Ask ShopX AI about this product,
                availability and more.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# SPECIFICATIONS
# =========================================================

st.divider()

st.markdown(
    '<div class="spec-title">⚙️ Specifications</div>',
    unsafe_allow_html=True,
)


specifications = (
    product.get("specifications") or {}
)


if specifications:

    for key, value in specifications.items():

        st.markdown(
            f"""
            <div class="spec-row">
                <strong>{key}</strong>
                <br>
                <span>{value}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

else:

    st.info(
        "No specifications are available for this product."
    )


# =========================================================
# ABOUT PRODUCT
# =========================================================

st.divider()

st.markdown(
    '<div class="spec-title">📖 About this product</div>',
    unsafe_allow_html=True,
)

st.write(
    description
)