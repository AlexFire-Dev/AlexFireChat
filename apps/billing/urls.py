from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy, include

from .views import *


urlpatterns = [
    path('new/', BillView.as_view(), name='bill-new'),
    path('success/', SuccessBillView.as_view(), name='bill-success'),
]
