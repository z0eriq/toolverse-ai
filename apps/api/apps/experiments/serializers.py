from rest_framework import serializers

from apps.experiments.models import Experiment


class ExperimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experiment
        fields = (
            "id",
            "key",
            "name",
            "description",
            "variants",
            "is_active",
            "created_at",
            "updated_at",
        )


class AssignQuerySerializer(serializers.Serializer):
    key = serializers.SlugField()
    subject_key = serializers.CharField(required=False, allow_blank=True, max_length=128)


class TrackEventSerializer(serializers.Serializer):
    key = serializers.SlugField()
    subject_key = serializers.CharField(max_length=128)
    event_name = serializers.CharField(max_length=128)
    properties = serializers.DictField(required=False, default=dict)
