class Utils:
    # format in same way as Django usually formats for templates
    @staticmethod
    def get_template_formatted_date(date):
        return date.strftime('%b. ' + str(date.day) + ', %Y')