import streamlit as st

from utils.auth import require_user, get_current_user_role
from utils.nav import render_sidebar
from utils.supabase_client import supabase


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Products - ShopX",
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
       PAGE HEADER
       ===================================================== */

    .products-title {
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 0.2rem;
    }

    .products-subtitle {
        color: #6b7280;
        font-size: 1.05rem;
        margin-bottom: 1.8rem;
    }


    /* =====================================================
       SEARCH AREA
       ===================================================== */

    .filter-label {
        font-size: 0.8rem;
        font-weight: 700;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }


    /* =====================================================
       PRODUCT CARD
       ===================================================== */

    .product-card {
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 1rem;
        background: white;
        margin-bottom: 1.2rem;
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.04);
    }

    .product-name {
        font-size: 1.15rem;
        font-weight: 700;
        margin-top: 0.7rem;
        margin-bottom: 0.25rem;
    }

    .product-meta {
        color: #6b7280;
        font-size: 0.85rem;
        margin-bottom: 0.5rem;
    }

    .product-price {
        font-size: 1.45rem;
        font-weight: 800;
        margin-top: 0.5rem;
        margin-bottom: 0.4rem;
    }


    /* =====================================================
       STOCK BADGES
       ===================================================== */

    .stock-available {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        background: #ecfdf5;
        color: #047857;
        font-size: 0.75rem;
        font-weight: 700;
    }

    .stock-low {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        background: #fff7ed;
        color: #c2410c;
        font-size: 0.75rem;
        font-weight: 700;
    }

    .stock-out {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        background: #fef2f2;
        color: #b91c1c;
        font-size: 0.75rem;
        font-weight: 700;
    }


    /* =====================================================
       RESULT COUNT
       ===================================================== */

    .result-count {
        color: #6b7280;
        font-size: 0.9rem;
        margin: 0.5rem 0 1rem 0;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# PAGE HEADER
# =========================================================

st.markdown(
    '<div class="products-title">🛍️ Products</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="products-subtitle">'
    'Discover products selected for your everyday needs.'
    '</div>',
    unsafe_allow_html=True,
)


# =========================================================
# FETCH PRODUCTS
# =========================================================

try:

    response = (
        supabase
        .table("products")
        .select("*")
        .order("id")
        .execute()
    )

    products = response.data or []

except Exception as e:

    st.error(
        f"Unable to load products: {e}"
    )

    st.stop()


# =========================================================
# EMPTY CATALOG
# =========================================================

if not products:

    st.info(
        "🛍️ No products are available right now."
    )

    st.stop()


# =========================================================
# SEARCH + FILTER
# =========================================================

search_col, category_col = st.columns(
    [2.5, 1]
)

with search_col:

    search = st.text_input(
        "Search",
        placeholder="🔍  Search by product, brand or description...",
        label_visibility="collapsed",
    )

with category_col:

    categories = sorted(
        list(
            set(
                product.get("category")
                for product in products
                if product.get("category")
            )
        )
    )

    selected_category = st.selectbox(
        "Category",
        ["All Categories"] + categories,
        label_visibility="collapsed",
    )


# =========================================================
# FILTER PRODUCTS
# =========================================================

filtered_products = products


if search:

    search_lower = search.lower().strip()

    filtered_products = [
        product
        for product in filtered_products
        if (
            search_lower in product.get("name", "").lower()
            or search_lower in product.get("brand", "").lower()
            or search_lower in product.get("description", "").lower()
            or search_lower in product.get("category", "").lower()
        )
    ]


if selected_category != "All Categories":

    filtered_products = [
        product
        for product in filtered_products
        if product.get("category") == selected_category
    ]


# =========================================================
# RESULTS HEADER
# =========================================================

st.markdown(
    f"""
    <div class="result-count">
        Showing <strong>{len(filtered_products)}</strong>
        product(s)
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# NO RESULTS
# =========================================================

if not filtered_products:

    st.warning(
        "🔎 No products match your search."
    )

    if st.button(
        "Clear Filters",
        use_container_width=False,
    ):

        st.rerun()

    st.stop()


# =========================================================
# PRODUCT GRID
# =========================================================

columns = st.columns(3)


for index, product in enumerate(filtered_products):

    with columns[index % 3]:

        # -------------------------------------------------
        # Product Card
        # -------------------------------------------------

        with st.container(border=True):

            # -------------------------------------------------
            # Image
            # -------------------------------------------------

            if product.get("image_url"):

                st.image(
                    product["image_url"],
                    use_container_width=True,
                )

            else:

                st.markdown(
                    """
                    <div style="
                        height: 220px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        background: #f8fafc;
                        border-radius: 12px;
                        font-size: 3rem;
                    ">
                        🛍️
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


            # -------------------------------------------------
            # Product Name
            # -------------------------------------------------

            st.markdown(
                f"""
                <div class="product-name">
                    {product.get("name", "Unnamed Product")}
                </div>
                """,
                unsafe_allow_html=True,
            )


            # -------------------------------------------------
            # Brand / Category
            # -------------------------------------------------

            st.markdown(
                f"""
                <div class="product-meta">
                    {product.get("brand", "Unknown Brand")}
                    &nbsp;•&nbsp;
                    {product.get("category", "Uncategorized")}
                </div>
                """,
                unsafe_allow_html=True,
            )


            # -------------------------------------------------
            # Rating
            # -------------------------------------------------

            rating = product.get("rating", 0) or 0

            st.write(
                f"⭐ {float(rating):.1f} / 5"
            )


            # -------------------------------------------------
            # Price
            # -------------------------------------------------

            price = float(
                product.get("price", 0)
            )

            st.markdown(
                f"""
                <div class="product-price">
                    ₹{price:,.0f}
                </div>
                """,
                unsafe_allow_html=True,
            )


            # -------------------------------------------------
            # Stock
            # -------------------------------------------------

            stock = int(
                product.get("stock", 0) or 0
            )

            if stock == 0:

                st.markdown(
                    '<span class="stock-out">'
                    'OUT OF STOCK'
                    '</span>',
                    unsafe_allow_html=True,
                )

            elif stock <= 5:

                st.markdown(
                    f'<span class="stock-low">'
                    f'ONLY {stock} LEFT'
                    f'</span>',
                    unsafe_allow_html=True,
                )

            else:

                st.markdown(
                    f'<span class="stock-available">'
                    f'{stock} IN STOCK'
                    f'</span>',
                    unsafe_allow_html=True,
                )


            st.write("")


            # -------------------------------------------------
            # View Product
            # -------------------------------------------------

            if st.button(
                "View Product →",
                key=f"view_product_{product['id']}",
                use_container_width=True,
            ):

                st.session_state[
                    "selected_product_id"
                ] = product["id"]

                st.switch_page(
                    "pages/product_details.py"
                )