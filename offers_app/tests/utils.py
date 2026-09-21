from offers_app.models import Offer, OfferDetail

TYPES = ['basic', 'standard', 'premium']


def detail_payload(offer_type, price=100, days=5):
    """Return the request body of one package."""
    return {
        'title': f'{offer_type.title()} Design',
        'revisions': 2,
        'delivery_time_in_days': days,
        'price': price,
        'features': ['Logo Design', 'Business Card'],
        'offer_type': offer_type,
    }


def offer_payload(title='Graphic design'):
    """Return a valid request body with all three packages."""
    return {
        'title': title,
        'image': None,
        'description': 'A complete design package.',
        'details': [
            detail_payload('basic', 100, 5),
            detail_payload('standard', 200, 7),
            detail_payload('premium', 500, 10),
        ],
    }


def create_offer(user, title='Graphic design', prices=(100, 200, 500),
                 days=(5, 7, 10), description='A complete design package.'):
    """Create an offer with its three packages straight in the database."""
    offer = Offer.objects.create(
        user=user, title=title, description=description,
    )
    for offer_type, price, day in zip(TYPES, prices, days):
        OfferDetail.objects.create(
            offer=offer, **detail_payload(offer_type, price, day),
        )
    return offer
