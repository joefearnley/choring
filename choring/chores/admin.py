

# Register your models here.

from django.contrib import admin

from .models import Chore
from .models import ChoreOccurrence
from django import forms
from django.urls import path
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.contrib import messages
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
	list_display = ('title', 'assigned_to', 'due_date', 'next_occurrence_display', 'recurrence', 'active')
	list_filter = ('recurrence', 'active', 'assigned_to', ('due_date', admin.DateFieldListFilter))
	search_fields = ('title', 'description', 'assigned_to__username', 'assigned_to__email')
	list_editable = ('assigned_to', 'active')
	list_select_related = ('assigned_to',)
	date_hierarchy = 'due_date'
	ordering = ('-created_at', 'title')
	readonly_fields = ('created_at', 'next_occurrence_display')
	fieldsets = (
		(None, {'fields': ('title', 'description')}),
		('Assignment', {'fields': ('assigned_to', 'active')}),
		('Scheduling', {'fields': ('start_date', 'due_date', 'recurrence', 'next_occurrence_display')}),
		('Timestamps', {'fields': ('created_at',)}),
	)
	actions = ('mark_active', 'mark_inactive', 'unassign')

	def get_queryset(self, request):
		qs = super().get_queryset(request)
		return qs.select_related('assigned_to')

	def next_occurrence_display(self, obj):
		from datetime import date

		try:
			nxt = obj.next_occurrence_after(date.today())
		except Exception:
			return '-'
		return nxt or '-'

	next_occurrence_display.short_description = 'Next Occurrence'

	@admin.action(description='Mark selected chores as active')
	def mark_active(self, request, queryset):
		queryset.update(active=True)

	@admin.action(description='Mark selected chores as inactive')
	def mark_inactive(self, request, queryset):
		queryset.update(active=False)

	@admin.action(description='Unassign selected chores')
	def unassign(self, request, queryset):
		queryset.update(assigned_to=None)

	def get_urls(self):
		urls = super().get_urls()
		custom = [
			path('generate-occurrences/', self.admin_site.admin_view(self.generate_occurrences_view), name='chore-generate-occurrences'),
		]
		return custom + urls

	def generate_occurrences_action(self, request, queryset):
		ids = ",".join(str(o.pk) for o in queryset)
		return redirect(f"./generate-occurrences/?ids={ids}")

	actions = ('mark_active', 'mark_inactive', 'unassign', 'generate_occurrences_action')

	class GenerateOccurrencesForm(forms.Form):
		start_date = forms.DateField()
		end_date = forms.DateField()
		ids = forms.CharField(widget=forms.HiddenInput)

	def generate_occurrences_view(self, request):
		ids = request.GET.get('ids') or request.POST.get('ids')
		if not ids:
			messages.error(request, 'No chores selected')
			return redirect('..')

		if request.method == 'POST':
			form = self.GenerateOccurrencesForm(request.POST)
			if form.is_valid():
				start = form.cleaned_data['start_date']
				end = form.cleaned_data['end_date']
				id_list = [int(x) for x in form.cleaned_data['ids'].split(',') if x]
				chores = Chore.objects.filter(pk__in=id_list)
				created = 0
				for chore in chores:
					# compute first occurrence on or after start
					nxt = chore.next_occurrence_after(start)
					while nxt and nxt <= end:
						obj, created_flag = ChoreOccurrence.objects.get_or_create(
							chore=chore,
							occurrence_date=nxt,
							defaults={'assigned_to': chore.assigned_to}
						)
						if created_flag:
							created += 1
						# advance
						if chore.recurrence == chore.RECURRENCE_WEEKLY:
							nxt = nxt + timedelta(days=7)
						elif chore.recurrence == chore.RECURRENCE_MONTHLY:
							nxt = nxt + relativedelta(months=1)
						else:
							break

				messages.success(request, f'Created {created} occurrences')
				return redirect('..')
		else:
			form = self.GenerateOccurrencesForm(initial={'ids': ids})

		context = dict(
			self.admin_site.each_context(request),
			title='Generate Chore Occurrences',
			form=form,
			opts=self.model._meta,
		)
		return TemplateResponse(request, 'admin/chores/generate_occurrences.html', context)


# Small admin site branding tweaks
admin.site.site_header = 'Choring Administration'
admin.site.site_title = 'Choring Admin'
admin.site.index_title = 'Site Administration'


@admin.register(ChoreOccurrence)
class ChoreOccurrenceAdmin(admin.ModelAdmin):
	list_display = ('chore', 'occurrence_date', 'assigned_to', 'created_at')
	list_filter = ('occurrence_date', 'assigned_to')
	search_fields = ('chore__title', 'assigned_to__username', 'assigned_to__email')
