class Utils:
    # format in same way as Django usually formats for templates
    @staticmethod
    def get_template_formatted_date(date):
        return date.strftime(str(month(date.month)) + ' ' + str(date.day) + ', %Y')


def month(index):
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
