import streamlit as st


def initialize_cart():
    """Initialize the shopping cart in Streamlit session state."""
    if "cart" not in st.session_state:
        st.session_state.cart = {}


def add_to_cart(product_id, quantity=1):
    """Add a product to the cart."""
    initialize_cart()

    if product_id in st.session_state.cart:
        st.session_state.cart[product_id] += quantity
    else:
        st.session_state.cart[product_id] = quantity


def remove_from_cart(product_id):
    """Remove a product completely from the cart."""
    initialize_cart()

    if product_id in st.session_state.cart:
        del st.session_state.cart[product_id]


def update_quantity(product_id, quantity):
    """Update product quantity."""
    initialize_cart()

    if quantity <= 0:
        remove_from_cart(product_id)
    else:
        st.session_state.cart[product_id] = quantity


def get_cart_count():
    """Return total number of items in the cart."""
    initialize_cart()

    return sum(st.session_state.cart.values())


def clear_cart():
    """Remove all items from the cart."""
    st.session_state.cart = {}