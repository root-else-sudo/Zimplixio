from django.contrib import admin
from .models import TechTag, ShowcaseProject, ShowcaseScreenshot


@admin.register(TechTag)
class TechTagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


class ShowcaseScreenshotInline(admin.TabularInline):
    model = ShowcaseScreenshot
    extra = 1


@admin.register(ShowcaseProject)
class ShowcaseProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'industry', 'is_published', 'order', 'updated_at']
    list_filter = ['is_published', 'industry']
    search_fields = ['title', 'summary']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tech_tags']
    inlines = [ShowcaseScreenshotInline]
    fieldsets = [
        (None, {
            'fields': ('title', 'slug', 'summary', 'thumbnail', 'industry', 'tech_tags', 'is_published', 'order'),
        }),
        ('Case Study Content', {
            'classes': ('collapse',),
            'fields': ('business_problem', 'approach', 'solution_description', 'architecture_diagram', 'outcomes', 'demo_url'),
        }),
    ]
