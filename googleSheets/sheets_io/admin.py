from django.contrib import admin

# Register your models here.
from .models import Log


class LogAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Expand', {
            'classes': ('collapse',),
            'fields': (('from_sheet', 'to_sheet', 'from_tab', 'to_tab',  'updated_row', 'updated_col', 'updated_range'), )
        }),
    )
    # fieldsets =('None',{fields = (('from_sheet', 'to_sheet', 'from_tab', 'to_tab',  'updated_row', 'updated_col', 'updated_range'))}, )
    list_filter = ('updated_at',)
    search_filter= ('from_sheet', 'to_sheet', 'from_tab', 'to_tab')


admin.site.register(Log, LogAdmin)
#password: googlesheet
#username: admin