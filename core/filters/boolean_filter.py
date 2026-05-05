import django_filters


class OnlyTrueFilter(django_filters.BooleanFilter):

    def filter(self, qs, value):
        if value is None:
            return qs

        if value is True:
            return super().filter(qs, value)

        return qs