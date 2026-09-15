import streamlit as st
from textwrap import dedent
from utils.supabase_client import supabase
from utils.cart import get_cart_count
from utils.auth import (
    is_authenticated,
    get_current_user_role,
)
from utils.nav import render_sidebar


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="ShopX",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* =========================
       GLOBAL
       ========================= */

    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        letter-spacing: -0.5px;
    }


    /* =========================
       SHOPX HEADER
       ========================= */

    .shopx-brand {
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -1.5px;
        margin-bottom: 0;
    }

    .shopx-tagline {
        color: #6b7280;
        font-size: 1rem;
        margin-top: -5px;
    }


    /* =========================
       WELCOME
       ========================= */

    .welcome-text {
        font-size: 1.05rem;
        color: #6b7280;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
    }


    /* =========================
       HERO
       ========================= */

    .hero-box {
        padding: 3.5rem 2rem;
        border-radius: 24px;
        background: linear-gradient(
            135deg,
            #f8fafc 0%,
            #eef2ff 100%
        );
        border: 1px solid #e5e7eb;
        text-align: center;
        margin: 1.5rem 0 2.5rem 0;
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.7rem;
    }

    .hero-description {
        font-size: 1.15rem;
        color: #6b7280;
        margin-bottom: 0;
    }


    /* =========================
       SECTION TITLE
       ========================= */

    .section-title {
        font-size: 1.8rem;
        font-weight: 750;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }


    /* =========================
       PRODUCT CARD
       ========================= */

    .product-card {
        padding: 1rem;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        background: white;
        min-height: 100%;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
    }


    /* =========================
       CATEGORY CARD
       ========================= */

    .category-card {
        padding: 1.5rem 1rem;
        border-radius: 18px;
        border: 1px solid #e5e7eb;
        background: #ffffff;
        text-align: center;
        transition: 0.2s ease;
        margin-bottom: 1rem;
    }

    .category-icon {
        font-size: 2.4rem;
        margin-bottom: 0.4rem;
    }

    .category-name {
        font-size: 1.05rem;
        font-weight: 650;
    }


    /* =========================
       WHY SHOPX
       ========================= */

    .feature-box {
        padding: 1.5rem;
        border-radius: 18px;
        border: 1px solid #e5e7eb;
        background: #f8fafc;
        min-height: 160px;
    }

    .feature-title {
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .feature-description {
        color: #6b7280;
        line-height: 1.6;
    }


    /* =========================
       FOOTER
       ========================= */

    .footer {
        text-align: center;
        color: #9ca3af;
        padding: 1rem 0;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# AUTHENTICATION
# =========================================================

if not is_authenticated():

    st.warning("Please login to access your ShopX account.")

    if st.button(
        "🔐 Login / Create Account",
        type="primary",
        use_container_width=True,
    ):
        st.switch_page("pages/login.py")

    st.stop()


# =========================================================
# CURRENT USER
# =========================================================

user = st.session_state.user
role = get_current_user_role()

render_sidebar(role)


# =========================================================
# ADMIN HOME REDIRECT
# =========================================================

if role == "admin":

    st.markdown(
        '<div class="shopx-brand">🛍️ ShopX</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="shopx-tagline">'
        'Store administration & AI knowledge management'
        '</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    st.info(
        "👋 You are logged in as an administrator. "
        "The customer storefront is available only to user accounts."
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button(
            "🛠️ Open Admin Dashboard",
            type="primary",
            use_container_width=True,
        ):
            st.switch_page("pages/admin.py")

    st.stop()


# =========================================================
# USER HOME
# =========================================================

user_name = user.user_metadata.get(
    "name",
    user.email.split("@")[0],
)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

header_left, header_right = st.columns([7, 3])

with header_left:

    st.markdown(
        '<div class="shopx-brand">🛍️ ShopX</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="shopx-tagline">'
        'Smart shopping powered by AI'
        '</div>',
        unsafe_allow_html=True,
    )


with header_right:

    button_col1, button_col2 = st.columns(2)

    with button_col1:

        if st.button(
            "🛍️ Products",
            use_container_width=True,
            key="home_products_btn",
        ):
            st.switch_page("pages/products.py")

    with button_col2:

        cart_count = get_cart_count()

        if st.button(
            f"🛒 Cart ({cart_count})",
            use_container_width=True,
            key="home_cart_btn",
        ):
            st.switch_page("pages/cart.py")


st.divider()


# =========================================================
# WELCOME
# =========================================================

st.markdown(
    f"""
    <div class="welcome-text">
        Welcome back, <strong>{user_name}</strong> 👋
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HERO
# =========================================================

# --------------------------------
# Hero Section
# --------------------------------

st.markdown(
    """
    <style>
    .shopx-hero {
        background: linear-gradient(135deg, #f5f7ff, #eef2ff);
        border: 1px solid #e1e6f5;
        border-radius: 22px;
        padding: 42px 48px;
        margin: 28px 0;
    }

    .shopx-hero h1 {
        font-size: 38px;
        font-weight: 750;
        margin: 0 0 12px 0;
    }

    .shopx-hero p {
        font-size: 17px;
        color: #667085;
        margin: 0;
        line-height: 1.6;
    }
    </style>

    <div class="shopx-hero">
        <h1>🛍️ Shop Smarter with ShopX</h1>
        <p>
            Discover quality products, great prices,
            and get instant help from our AI shopping assistant.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

hero_left, hero_center, hero_right = st.columns([2, 2, 2])

with hero_center:

    if st.button(
        "🛒 Explore Products",
        type="primary",
        use_container_width=True,
        key="shop_now_btn",
    ):
        st.switch_page("pages/products.py")


# =========================================================
# FEATURED PRODUCTS
# =========================================================

st.markdown(
    '<div class="section-title">⭐ Featured Products</div>',
    unsafe_allow_html=True,
)


try:

    response = (
        supabase
        .table("products")
        .select("*")
        .order("id")
        .limit(3)
        .execute()
    )

    featured_products = response.data or []

except Exception as e:

    st.error(f"Unable to load featured products: {e}")

    featured_products = []


if featured_products:

    columns = st.columns(3)

    for index, product in enumerate(featured_products):

        with columns[index]:

            with st.container(border=True):

                if product.get("image_url"):

                    st.image(
                        product["image_url"],
                        use_container_width=True,
                    )

                st.markdown(
                    f"### {product['name']}"
                )

                st.caption(
                    f"{product.get('brand', '')} • "
                    f"{product.get('category', '')}"
                )

                rating = product.get("rating", 0)

                st.write(
                    f"⭐ {rating} / 5"
                )

                st.markdown(
                    f"### ₹{float(product['price']):,.0f}"
                )

                stock = product.get("stock", 0)

                if stock > 0:

                    st.caption(
                        f"📦 {stock} unit(s) available"
                    )

                else:

                    st.error("Out of stock")

                if st.button(
                    "View Product →",
                    key=f"featured_{product['id']}",
                    use_container_width=True,
                ):

                    st.session_state[
                        "selected_product_id"
                    ] = product["id"]

                    st.switch_page(
                        "pages/product_details.py"
                    )

else:

    st.info("No featured products available.")


# =========================================================
# CATEGORIES
# =========================================================

st.divider()

st.markdown(
    '<div class="section-title">🏷️ Shop by Category</div>',
    unsafe_allow_html=True,
)


categories = [
    ("📱", "Smartphones"),
    ("🎧", "Audio"),
    ("💻", "Laptops"),
    ("⌚", "Wearables"),
    ("👟", "Footwear"),
    ("📱", "Tablets"),
]


category_columns = st.columns(3)


for index, (icon, category) in enumerate(categories):

    with category_columns[index % 3]:

        st.markdown(
            dedent(f"""
            <div class="category-card">
                <div class="category-icon">
                    {icon}
                </div>

                <div class="category-name">
                    {category}
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )

# =========================================================
# WHY SHOPX
# =========================================================

st.divider()

st.markdown(
    '<div class="section-title">💡 Why ShopX?</div>',
    unsafe_allow_html=True,
)


feature1, feature2, feature3 = st.columns(3)


with feature1:

    st.markdown(
        """
        <div class="feature-box">

            <div class="feature-title">
                🚚 Fast Delivery
            </div>

            <div class="feature-description">
                Get your products delivered quickly
                and reliably to your doorstep.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with feature2:

    st.markdown(
        """
        <div class="feature-box">

            <div class="feature-title">
                🔒 Secure Shopping
            </div>

            <div class="feature-description">
                Your account and shopping experience
                are protected with secure authentication.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with feature3:

    st.markdown(
        """
        <div class="feature-box">

            <div class="feature-title">
                🤖 AI Shopping Assistant
            </div>

            <div class="feature-description">
                Ask questions about products, policies,
                orders, delivery and more.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown(
    """
    <div class="footer">
        © 2026 ShopX · AI-powered e-commerce experience
    </div>
    """,
    unsafe_allow_html=True,
)