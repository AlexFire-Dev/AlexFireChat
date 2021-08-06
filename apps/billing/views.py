import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View, TemplateView, CreateView, UpdateView, RedirectView

from .models import *


class SuccessBillView(View):
    def post(self, request, *args, **kwargs):
        try:
            bill = Bill.objects.get(bill_id=request.POST['id'])
            bill.success()

            return HttpResponse('Ok!', status=202)
        except:
            return HttpResponse('Something went wrong!', status=500)
