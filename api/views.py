# Create your views here.
from rest_framework.generics import ListAPIView

from api.serializers import WorkshopSerializer
from workshop_app.models import Workshop


class UpcomingWorkshops(ListAPIView):
    serializer_class = WorkshopSerializer

    def get_queryset(self):
        params = self.request.GET
        queryset = Workshop.objects.all()
        if params.get('status', None):
            queryset = queryset.filter(status=params.get('status'))
        if params.get('date_from'):
            queryset = queryset.filter(date__gte=params.get('date_from'))
        if params.get('date_to'):
            queryset = queryset.filter(date__lte=params.get('date_to'))
        return queryset
