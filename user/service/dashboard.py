
from order.models import Order
from django.db.models import Count


class DashboardService:
    EXCLUDED_STATUSES = {"paid"}

    @staticmethod
    def get_order_stats(user):
        qs = (
            Order.objects
            .filter(created_by=user)
            .values("status")
            .annotate(count=Count("id"))
        )

        order_stats = {
            status: 0
            for status, _ in Order.STATUS_CHOICE
            if status not in DashboardService.EXCLUDED_STATUSES
        }

        for item in qs:
            if item["status"] not in DashboardService.EXCLUDED_STATUSES:
                order_stats[item["status"]] = item["count"]

        return order_stats