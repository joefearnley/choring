from django.contrib.auth.models import Group, User
from rest_framework import viewsets

from choring.chores.serializers import GroupSerializer, UserSerializer
from choring.chores.serializers import ChoreSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from .models import Chore
from .models import ChoreOccurrence
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from .models import UserProfile


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def chores_for_week(request):
    # Determine current week's Monday and Sunday
    today = date.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)

    results = []

    chores = Chore.objects.filter(active=True)
    # load any persisted occurrences in the week range
    persisted = ChoreOccurrence.objects.filter(occurrence_date__range=(start, end)).select_related('assigned_to', 'chore')
    persisted_map = {(o.chore_id, o.occurrence_date): o for o in persisted}
    for chore in chores:
        # non-recurring
        if chore.recurrence == Chore.RECURRENCE_NONE:
            if chore.due_date and start <= chore.due_date <= end:
                occ = persisted_map.get((chore.pk, chore.due_date))
                # Skip completed persisted occurrences so landing page only shows uncompleted
                if occ and occ.completed:
                    continue
                assigned = occ.assigned_to.username if occ and occ.assigned_to else (chore.assigned_to.username if chore.assigned_to else None)
                assigned_color = (
                    getattr(getattr(occ.assigned_to, 'userprofile', None), 'color', None) if occ and occ.assigned_to
                    else (getattr(getattr(chore.assigned_to, 'userprofile', None), 'color', None) if chore.assigned_to else None)
                )
                # normalize recurrence: treat None or explicit 'none' as empty string
                rec_val = '' if (chore.recurrence is None or chore.recurrence == Chore.RECURRENCE_NONE) else chore.recurrence
                results.append({
                    'date': chore.due_date,
                    'title': chore.title,
                    'chore_id': chore.pk,
                    'assigned_to': assigned,
                    'assigned_color': assigned_color,
                    'recurrence': rec_val,
                    'completed': False,
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
            # iterate occurrences up to end
            while current <= end:
                occ = persisted_map.get((chore.pk, current))
                # skip completed persisted occurrences
                if occ and occ.completed:
                    if chore.recurrence == Chore.RECURRENCE_WEEKLY:
                        current = current + timedelta(days=7)
                    else:
                        current = current + relativedelta(months=1)
                    continue
                assigned = occ.assigned_to.username if occ and occ.assigned_to else (chore.assigned_to.username if chore.assigned_to else None)
                assigned_color = (
                    getattr(getattr(occ.assigned_to, 'userprofile', None), 'color', None) if occ and occ.assigned_to
                    else (getattr(getattr(chore.assigned_to, 'userprofile', None), 'color', None) if chore.assigned_to else None)
                )
                rec_val = '' if (chore.recurrence is None or chore.recurrence == Chore.RECURRENCE_NONE) else chore.recurrence
                results.append({
                    'date': current,
                    'title': chore.title,
                    'chore_id': chore.pk,
                    'assigned_to': assigned,
                    'assigned_color': assigned_color,
                    'recurrence': rec_val,
                    'completed': False,
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


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def chores_for_range(request):
    """Return chore occurrences between `start` and `end` (ISO dates)."""
    qs_start = request.GET.get('start')
    qs_end = request.GET.get('end')
    today = date.today()
    try:
        if qs_start:
            start = date.fromisoformat(qs_start)
        else:
            start = today - timedelta(days=28)
        if qs_end:
            end = date.fromisoformat(qs_end)
        else:
            end = today + timedelta(days=28)
    except Exception:
        return Response({'detail': 'invalid date'}, status=400)

    results = []
    chores = Chore.objects.filter(active=True)
    persisted = ChoreOccurrence.objects.filter(occurrence_date__range=(start, end)).select_related('assigned_to', 'chore')
    persisted_map = {(o.chore_id, o.occurrence_date): o for o in persisted}
    for chore in chores:
        if chore.recurrence == Chore.RECURRENCE_NONE:
            if chore.due_date and start <= chore.due_date <= end:
                occ = persisted_map.get((chore.pk, chore.due_date))
                # Skip completed persisted occurrences so landing page only shows uncompleted
                if occ and occ.completed:
                    continue
                assigned = occ.assigned_to.username if occ and occ.assigned_to else (chore.assigned_to.username if chore.assigned_to else None)
                assigned_color = (
                    getattr(getattr(occ.assigned_to, 'userprofile', None), 'color', None) if occ and occ.assigned_to
                    else (getattr(getattr(chore.assigned_to, 'userprofile', None), 'color', None) if chore.assigned_to else None)
                )
                rec_val = '' if (chore.recurrence is None or chore.recurrence == Chore.RECURRENCE_NONE) else chore.recurrence
                results.append({
                    'date': chore.due_date,
                    'title': chore.title,
                    'chore_id': chore.pk,
                    'assigned_to': assigned,
                    'assigned_color': assigned_color,
                    'recurrence': rec_val,
                    'completed': False,
                })
        else:
            base = chore.start_date or chore.due_date
            if not base:
                continue
            current = base
            while current < start:
                if chore.recurrence == chore.RECURRENCE_WEEKLY:
                    current = current + timedelta(days=7)
                else:
                    current = current + relativedelta(months=1)
            while current <= end:
                occ = persisted_map.get((chore.pk, current))
                # skip completed persisted occurrences
                if occ and occ.completed:
                    if chore.recurrence == chore.RECURRENCE_WEEKLY:
                        current = current + timedelta(days=7)
                    else:
                        current = current + relativedelta(months=1)
                    continue
                assigned = occ.assigned_to.username if occ and occ.assigned_to else (chore.assigned_to.username if chore.assigned_to else None)
                assigned_color = (
                    getattr(getattr(occ.assigned_to, 'userprofile', None), 'color', None) if occ and occ.assigned_to
                    else (getattr(getattr(chore.assigned_to, 'userprofile', None), 'color', None) if chore.assigned_to else None)
                )
                rec_val = '' if (chore.recurrence is None or chore.recurrence == Chore.RECURRENCE_NONE) else chore.recurrence
                results.append({
                    'date': current,
                    'title': chore.title,
                    'chore_id': chore.pk,
                    'assigned_to': assigned,
                    'assigned_color': assigned_color,
                    'recurrence': rec_val,
                    'completed': False,
                })
                if chore.recurrence == chore.RECURRENCE_WEEKLY:
                    current = current + timedelta(days=7)
                else:
                    current = current + relativedelta(months=1)

    results.sort(key=lambda r: r['date'])
    for r in results:
        r['date'] = r['date'].isoformat()
    return Response(results)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def badge_colors(request):
    """Return available Tailwind color keys for frontend pickers."""
    colors = [{'key': c[0], 'label': c[1]} for c in UserProfile.COLOR_CHOICES]
    return Response(colors)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def complete_occurrence(request):
    """Mark a chore occurrence as completed (create or update ChoreOccurrence).

    Expected JSON: {"chore_id": <id>, "date": "YYYY-MM-DD"}
    """
    data = request.data if hasattr(request, 'data') else request.POST
    chore_id = data.get('chore_id')
    date_s = data.get('date')
    if not chore_id or not date_s:
        return Response({'detail': 'chore_id and date required'}, status=400)
    try:
        occ_date = date.fromisoformat(date_s)
    except Exception:
        return Response({'detail': 'invalid date'}, status=400)
    try:
        chore = Chore.objects.get(pk=int(chore_id))
    except Chore.DoesNotExist:
        return Response({'detail': 'chore not found'}, status=404)

    occ, created = ChoreOccurrence.objects.get_or_create(chore=chore, occurrence_date=occ_date, defaults={'assigned_to': chore.assigned_to})
    from django.utils import timezone
    occ.completed = True
    occ.completed_at = timezone.now()
    occ.save()

    return Response({'chore_id': chore.pk, 'date': occ.occurrence_date.isoformat(), 'completed': True})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def completed_list(request):
    """Return the last 20 completed occurrences."""
    occs = ChoreOccurrence.objects.filter(completed=True).select_related('chore', 'assigned_to').order_by('-completed_at')[:20]
    results = []
    for o in occs:
        results.append({
            'chore_id': o.chore_id,
            'title': o.chore.title,
            'date': o.occurrence_date.isoformat(),
            'assigned_to': o.assigned_to.username if o.assigned_to else None,
            'assigned_color': getattr(getattr(o.assigned_to, 'userprofile', None), 'color', None) if o.assigned_to else None,
            'completed_at': o.completed_at.isoformat() if o.completed_at else None,
        })
    return Response(results)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def uncomplete_occurrence(request):
    data = request.data if hasattr(request, 'data') else request.POST
    chore_id = data.get('chore_id')
    date_s = data.get('date')
    if not chore_id or not date_s:
        return Response({'detail': 'chore_id and date required'}, status=400)
    try:
        occ_date = date.fromisoformat(date_s)
    except Exception:
        return Response({'detail': 'invalid date'}, status=400)
    try:
        occ = ChoreOccurrence.objects.get(chore_id=int(chore_id), occurrence_date=occ_date)
    except ChoreOccurrence.DoesNotExist:
        return Response({'detail': 'occurrence not found'}, status=404)
    occ.completed = False
    occ.completed_at = None
    occ.save()
    return Response({'chore_id': occ.chore_id, 'date': occ.occurrence_date.isoformat(), 'completed': False})


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
