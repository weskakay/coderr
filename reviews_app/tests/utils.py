from reviews_app.models import Review


def create_review(business, reviewer, rating=4, text='Good work.'):
    """Create a review straight in the database."""
    return Review.objects.create(
        business_user=business, reviewer=reviewer, rating=rating,
        description=text,
    )
