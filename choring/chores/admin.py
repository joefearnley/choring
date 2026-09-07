

# Register your models here.

from django.contrib import admin

from .models import Chore


@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
	list_display = ('title', 'assigned_to', 'due_date', 'recurrence', 'active')
	list_filter = ('recurrence', 'active', 'assigned_to')
	search_fields = ('title', 'description', 'assigned_to__username', 'assigned_to__email')
	list_editable = ('assigned_to', 'active')
	date_hierarchy = 'due_date'
	ordering = ('-created_at', 'title')
	actions = ('mark_active', 'mark_inactive', 'unassign')

	@admin.action(description='Mark selected chores as active')
	def mark_active(self, request, queryset):
		queryset.update(active=True)

	@admin.action(description='Mark selected chores as inactive')
	def mark_inactive(self, request, queryset):
		queryset.update(active=False)

	@admin.action(description='Unassign selected chores')
	def unassign(self, request, queryset):
		queryset.update(assigned_to=None)


# Small admin site branding tweaks
admin.site.site_header = 'Choring Administration'
admin.site.site_title = 'Choring Admin'
admin.site.index_title = 'Site Administration'
