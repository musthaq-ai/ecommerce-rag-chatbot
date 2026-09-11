import streamlit as st

st.set_page_config(
    page_title="ShopX",
    page_icon="🛍️",
    layout="wide"
)

st.title("🛍️ ShopX")

st.subheader("Welcome to ShopX")

st.write(
    "Your simple e-commerce store powered by modern AI."
)

st.info(
    "Browse our products and find what you need."
)

st.divider()

st.markdown("### Explore our store")

if st.button("🛒 Explore Products"):
    st.switch_page("pages/products.py")