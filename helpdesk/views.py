from rest_framework import generics, viewsets, status
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from helpdesk.models import Department, Ticket
from helpdesk.serializers import (
    DepartmentSerializer,
    TicketCreateSerializer,
    TicketDetailSerializer,
    TicketListSerializer,
    TicketMessageCreateSerializer,
)
# Create your views here.


@extend_schema(
    summary="List active departments",
    description="Returns list of active departments for ticket creation dropdown.",
    tags=["Helpdesk"],
)
class DepartmentListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = DepartmentSerializer
    queryset = Department.objects.filter(is_active=True)


@extend_schema_view(
    list=extend_schema(
        summary="List user tickets",
        description="Returns tickets of current user. Admin sees all tickets.",
        tags=["Helpdesk"],
    ),
    retrieve=extend_schema(
        summary="Retrieve ticket detail",
        description="Returns full ticket detail including messages.",
        tags=["Helpdesk"],
    ),
    create=extend_schema(
        summary="Create ticket",
        description="Create a new ticket. `created_by` is automatically set from logged-in user.",
        tags=["Helpdesk"],
    ),
)
class TicketViewSet(viewsets.ModelViewSet):
    lookup_field = "ticket_number"

    def get_queryset(self):

        user = self.request.user

        if user.is_superuser:
            queryset = Ticket.objects.filter(status=Ticket.Status.OPEN)
        else:
            queryset = Ticket.objects.filter(created_by=user)

        if self.action == "list":
            return queryset.select_related("department")
        if self.action == "retrieve":
            return queryset.prefetch_related("messages")
        return queryset

    def get_serializer_class(self):

        mapping = {
            "list": TicketListSerializer,
            "retrieve": TicketDetailSerializer,
            "create": TicketCreateSerializer,
        }
        return mapping.get(self.action, TicketListSerializer)

    @extend_schema(
        summary="Send ticket message",
        description="Adds a new message to a ticket. Sender is automatically set as current user.",
        tags=["Helpdesk"],
    )
    @action(detail=True,methods=["POST"],url_path="message",serializer_class=TicketMessageCreateSerializer,)
    def send_message(self, request, ticket_number):

        ticket = self.get_object()

        serializer = self.serializer_class(
            data=request.data, context={"ticket": ticket}
        )
        serializer.is_valid(raise_exception=True)

        serializer.save(ticket=ticket, created_by=request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


