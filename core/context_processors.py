def cart_context(request):
    """
    Makes the cart count available on all pages.
    """
    cart = request.session.get('cart', {})
    cart_count = 0

    # Correctly loop over items, skipping metadata keys
    for key, item in cart.items():
        if key not in ['restaurant_id', 'restaurant_name']:
            try:
                cart_count += item.get('quantity', 0)
            except AttributeError:
                # Handle cases where an item might be malformed (e.g., just an int)
                pass

    return {'cart_count': cart_count}
