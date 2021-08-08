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


class BillView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return self.url

    def get(self, request, *args, **kwargs):
        try:
            amount = float(request.GET.get('amount', '1.00'))
            comment = request.GET.get('comment', '')
            bill = Bill.objects.create(amount=amount, comment=comment)
            self.url = bill.get_url()

            return super(BillView, self).get(self, request, *args, **kwargs)
        except:
            return HttpResponse('Something went wrong!', status=400)
