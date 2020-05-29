# Create your views here.
import dateutil.parser
from rest_framework.generics import ListAPIView

from api.serializers import WorkshopSerializer
from workshop_app.models import Workshop


class UpcomingWorkshops(ListAPIView):
    serializer_class = WorkshopSerializer

    def get_queryset(self):
        params = self.request.GET
        queryset = Workshop.objects.all()
        if params.get('status', None):
            try:
                queryset = queryset.filter(status=params.get('status'))
            except:
                pass
        if params.get('date_from'):
            try:
                queryset = queryset.filter(date__gte=dateutil.parser.parse(params.get('date_from')).date())
            except:
                pass
        if params.get('date_to'):
            try:
                queryset = queryset.filter(date__lte=params.get('date_to'))
            except:
                pass
        return queryset
