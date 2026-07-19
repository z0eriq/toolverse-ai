from django.contrib import admin

from apps.experiments.models import Experiment, ExperimentAssignment, ExperimentEvent


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = ("key", "name", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("key", "name")


@admin.register(ExperimentAssignment)
class ExperimentAssignmentAdmin(admin.ModelAdmin):
    list_display = ("experiment", "subject_key", "variant", "created_at")
    list_filter = ("variant",)
    search_fields = ("subject_key",)
    raw_id_fields = ("experiment", "user")


@admin.register(ExperimentEvent)
class ExperimentEventAdmin(admin.ModelAdmin):
    list_display = ("experiment", "event_name", "variant", "subject_key", "created_at")
    list_filter = ("event_name",)
    raw_id_fields = ("experiment", "assignment")
