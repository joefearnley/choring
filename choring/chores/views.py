from django.contrib.auth.models import Group, User
from rest_framework import viewsets

from choring.chores.serializers import GroupSerializer, UserSerializer
from choring.chores.serializers import ChoreSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from .models import Chore
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def chores_for_week(request):
    # Determine current week's Monday and Sunday
    today = date.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)

    results = []

    chores = Chore.objects.filter(active=True)
    for chore in chores:
        # non-recurring
        if chore.recurrence == Chore.RECURRENCE_NONE:
            if chore.due_date and start <= chore.due_date <= end:
                results.append({
                    'date': chore.due_date,
                    'title': chore.title,
                    'assigned_to': chore.assigned_to.username if chore.assigned_to else None,
                    'recurrence': chore.recurrence,
                })
        else:
            # generate occurrences between start and end
            base = chore.start_date or chore.due_date
            if not base:
                continue
            current = base
            # advance to first occurrence >= start
            while current < start:
                if chore.recurrence == Chore.RECURRENCE_WEEKLY:
                    current = current + timedelta(days=7)
                else:
                    current = current + relativedelta(months=1)
            while current <= end:
                results.append({
                    'date': current,
                    'title': chore.title,
                    'assigned_to': chore.assigned_to.username if chore.assigned_to else None,
                    'recurrence': chore.recurrence,
                })
                if chore.recurrence == Chore.RECURRENCE_WEEKLY:
                    current = current + timedelta(days=7)
                else:
                    current = current + relativedelta(months=1)

    # sort by date
    results.sort(key=lambda r: r['date'])
    # serialize dates to ISO
    for r in results:
        r['date'] = r['date'].isoformat()
    return Response(results)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
