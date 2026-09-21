class IdConverter:
    """Path converter for database ids.

    At most 18 digits, so a huge id gives a 404 instead of an integer
    overflow in the database.
    """

    regex = '[0-9]{1,18}'

    def to_python(self, value):
        """Turn the URL part into an int."""
        return int(value)

    def to_url(self, value):
        """Turn an id back into its URL part."""
        return str(value)
