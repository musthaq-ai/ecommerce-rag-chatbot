import streamlit as st
from data.products import products
from utils.cart import get_cart_count


st.set_page_config(
    page_title="ShopX",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==========================================
# Custom CSS
# ==========================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }

    .hero {
        padding: 3rem;
        border-radius: 20px;
        text-align: center;
        background-color: #f5f7fa;
        margin-bottom: 2rem;
    }

    .hero h1 {
        font-size: 3rem;
    }

    .hero p {
        font-size: 1.2rem;
    }

    .category-card {
        padding: 1.5rem;
        border-radius: 15px;
        background-color: #f5f7fa;
        text-align: center;
        margin-bottom: 1rem;
    }

    .category-icon {
        font-size: 2.5rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================
# Header
# ==========================================

header_col1, header_col2, header_col3 = st.columns(
    [5, 1, 1]
)

with header_col1:

    st.markdown(
        '<div class="main-title">🛍️ ShopX</div>',
        unsafe_allow_html=True
    )

with header_col2:

    if st.button("Products", use_container_width=True):
        st.switch_page("pages/products.py")

with header_col3:

    cart_count = get_cart_count()

    if st.button(
        f"🛒 Cart ({cart_count})",
        use_container_width=True
    ):
        st.switch_page("pages/cart.py")


st.divider()


# ==========================================
# Hero Section
# ==========================================

st.markdown(
    """
    <div class="hero">

        <h1>🛍️ Shop Smarter with ShopX</h1>

        <p>
        Discover quality products at great prices.
        </p>

    </div>
    """,
    unsafe_allow_html=True
)


hero_col1, hero_col2, hero_col3 = st.columns(
    [2, 1, 2]
)

with hero_col2:

    if st.button(
        "🛒 Shop Now",
        use_container_width=True
    ):

        st.switch_page("pages/products.py")


# ==========================================
# Featured Products
# ==========================================

st.markdown("## ⭐ Featured Products")

featured_products = products[:3]

columns = st.columns(3)

for index, product in enumerate(featured_products):

    with columns[index]:

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

        if st.button(
            "View Product",
            key=f"featured_{product['id']}",
            use_container_width=True
        ):

            st.session_state["selected_product_id"] = product["id"]

            st.switch_page(
                "pages/product_details.py"
            )


# ==========================================
# Categories
# ==========================================

st.divider()

st.markdown("## 🏷️ Shop by Category")

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
            f"""
            <div class="category-card">

                <div class="category-icon">
                    {icon}
                </div>

                <h3>{category}</h3>

            </div>
            """,
            unsafe_allow_html=True
        )


# ==========================================
# Why ShopX?
# ==========================================

st.divider()

st.markdown("## 💡 Why ShopX?")

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown("### 🚚 Fast Delivery")

    st.write(
        "Get your products delivered quickly "
        "and reliably."
    )


with col2:

    st.markdown("### 🔒 Secure Shopping")

    st.write(
        "Your account and shopping experience "
        "are designed with security in mind."
    )


with col3:

    st.markdown("### 🤖 AI Assistance")

    st.write(
        "Get instant help from our AI shopping "
        "assistant."
    )


# ==========================================
# Footer
# ==========================================

st.divider()

st.caption(
    "© 2026 ShopX — AI-powered e-commerce experience"
)