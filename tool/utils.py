class Utils:
    @staticmethod
    def get_template_formatted_date(date):
        """Format date in same way as Django usually formats for templates.
        e.g. 01/01/2020 -> Jan. 1, 2020

        :param date: date object to convert to formatted string
        :return: formatted string representing date in Django format
        """
        return date.strftime(str(month(date.month)) + ' ' + str(date.day) + ', %Y')


def month(index):
    """Get month string for a given month's index.

    :param index: index of the month in the year
    :return: string representing the month as Django formats them in templates
    """
    return {
        1: 'Jan.',
        2: 'Feb.',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'Aug.',
        9: 'Sept.',
        10: 'Oct.',
        11: 'Nov.',
        12: 'Dec.'
    }.get(index)
