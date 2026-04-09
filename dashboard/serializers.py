from rest_framework import serializers


class TicketsByPrioritySerializer(serializers.Serializer):
    priority = serializers.CharField()
    count = serializers.IntegerField()


class TicketsByProjectSerializer(serializers.Serializer):
    project__id = serializers.IntegerField()
    project__name = serializers.CharField()
    count = serializers.IntegerField()


class TicketsByStatusSerializer(serializers.Serializer):
    status = serializers.CharField()
    count = serializers.IntegerField()


class TicketsPerEmployeeSerializer(serializers.Serializer):
    assigned_to__id = serializers.IntegerField()
    assigned_to__username = serializers.CharField()
    assigned_to__full_name = serializers.CharField()
    count = serializers.IntegerField()


class DashboardStatsSerializer(serializers.Serializer):
    total_tickets = serializers.IntegerField()
    open_tickets = serializers.IntegerField()
    resolved_tickets = serializers.IntegerField()
    closed_tickets = serializers.IntegerField()
    tickets_by_priority = TicketsByPrioritySerializer(many=True)
    tickets_by_project = TicketsByProjectSerializer(many=True)
    tickets_by_status = TicketsByStatusSerializer(many=True)
    tickets_per_employee = TicketsPerEmployeeSerializer(many=True)
    active_projects_count = serializers.IntegerField()
    average_resolution_time_seconds = serializers.FloatField()
