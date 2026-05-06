from rest_framework import serializers

from helpdesk.models import Department, Ticket, TicketMessage


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = [
            "id",
            "name",
        ]


class TicketListSerializer(serializers.ModelSerializer):
    department = serializers.CharField(source="department.name")
    last_change = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            "ticket_number",
            "title",
            "department",
            "status",
            "priority",
            "last_change",
        ]

    def get_last_change(self, obj):

        if obj.status == Ticket.Status.CLOSED:
            return "Closed"

        user = self.context["request"].user
        last_message = obj.messages.order_by("-created_at").first()

        if not last_message:
            return "No Messages"

        if user.is_superuser and (not last_message.is_admin):
            return "Pending Review"

        if last_message.is_admin:
            return "Replied"

        return "In Progress"


class TicketCreateSerializer(serializers.ModelSerializer):
    ticket_number = serializers.IntegerField(read_only = True)
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    description = serializers.CharField(required=True, write_only=True)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True)
    )

    class Meta:
        model = Ticket
        fields = [
            "ticket_number",
            "created_by",
            "title",
            "department",
            "priority",
            "reference_code",
            "description",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        if Ticket.objects.filter(created_by=user, status=Ticket.Status.OPEN).exists():
            raise serializers.ValidationError({"message":"You already have an open ticket."})

        description = validated_data.pop("description")
        ticket = Ticket.objects.create(
            **validated_data,
            status=Ticket.Status.OPEN,
        )

        TicketMessage.objects.create(
            ticket=ticket,
            created_by=user,
            message=description,
            is_admin=True if user.is_superuser else False,
        )

        return ticket


class TicketMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketMessage
        fields = [
            "is_admin",
            "message",
            "created_at",
        ]


class TicketDetailSerializer(serializers.ModelSerializer):
    department = serializers.CharField(source="department.name")
    messages = TicketMessageSerializer(many=True)

    class Meta:
        model = Ticket
        fields = [
            "ticket_number",
            "title",
            "department",
            "status",
            "priority",
            "reference_code",
            "created_at",
            "messages",
        ]


class TicketMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketMessage
        fields = ["message"]

    def validate(self, attrs):

        ticket = self.context.get("ticket")

        if ticket.status == Ticket.Status.CLOSED:
            raise serializers.ValidationError(
                "This ticket is closed and no new messages can be sent."
            )

        if ticket.messages.count() >= 10:
            ticket.status = Ticket.Status.CLOSED
            ticket.save()
            raise serializers.ValidationError(
                "The number of messages for this ticket has reached the maximum allowed limit (20 messages)."
            )

        return attrs

    def create(self, validated_data):

        ticket = validated_data["ticket"]

        user = validated_data["created_by"]

        if user.is_superuser and not ticket.assigned_to:
            ticket.assigned_to = user
            ticket.save()

        return TicketMessage.objects.create(
            ticket=ticket,
            message=validated_data["message"],
            created_by=user,
            is_admin=True if user.is_superuser else False,
        )
