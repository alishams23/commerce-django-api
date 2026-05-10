from django.urls import path

from helpdesk.views import DepartmentListView, TicketViewSet

from rest_framework.routers import DefaultRouter

urlpatterns = [
    path("departments/", DepartmentListView.as_view(), name="departments"),
]


router = DefaultRouter()

router.register("tickets", TicketViewSet, basename="tickets")

urlpatterns += router.urls
