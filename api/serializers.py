from rest_framework import serializers

from workshop_app.models import Workshop, WorkshopType


class WorkshopTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkshopType
        exclude = ['terms_and_conditions']


class WorkshopTypeField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        pk = super(WorkshopTypeField, self).to_representation(value)
        items = WorkshopType.objects.filter(pk=pk)
        if items.exists():
            serializer = WorkshopTypeSerializer(items.first())
            return serializer.data
        else:
            return None


class WorkshopSerializer(serializers.ModelSerializer):
    workshop_type = WorkshopTypeField(read_only=True)

    class Meta:
        model = Workshop
        exclude = ['tnc_accepted']
