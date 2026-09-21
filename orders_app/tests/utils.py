from orders_app.models import Order


def create_order(customer, business, status=Order.IN_PROGRESS, **extra):
    """Create an order straight in the database."""
    data = {
        'title': 'Logo Design', 'revisions': 3, 'delivery_time_in_days': 5,
        'price': 150, 'features': ['Logo Design'], 'offer_type': 'basic',
    }
    data.update(extra)
    return Order.objects.create(
        customer_user=customer, business_user=business, status=status,
        **data,
    )
