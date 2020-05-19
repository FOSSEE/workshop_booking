# Create your views here.
from rest_framework.generics import ListAPIView

from api.serializers import WorkshopSerializer
from workshop_app.models import Workshop


class UpcomingWorkshops(ListAPIView):
    serializer_class = WorkshopSerializer

    def get_queryset(self):
        if self.request.GET.get('status', None):
            return Workshop.objects.filter(status=self.request.GET.get('status'))
        return Workshop.objects.all()
