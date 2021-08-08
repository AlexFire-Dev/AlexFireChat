import json

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View, TemplateView, CreateView, UpdateView, RedirectView

from .models import *


class SuccessBillView(View):
    def post(self, request, *args, **kwargs):
        import hmac
        import hashlib

        try:
            r_id = request.POST['id']
            r_status = request.POST['status']
            r_currency = request.POST['amount']['currency']
            r_value = request.POST['amount']['value']

            secret_key = bytes(settings.OPLATA_KEY)
            message = bytes(f'{r_id}|{r_status}|{r_currency}|{r_value}')

            my_signature = hmac.new(secret_key, message, hashlib.sha256).hexdigest()
            http_signature = request.headers.get('X-Api-Signature-SHA256').decode('UTF-8')

            if my_signature == http_signature:
                bill = Bill.objects.get(bill_id=r_id)
                bill.success()

                return HttpResponse('Ok!', status=202)
            else:
                return HttpResponse('Signature is incorrect!', status=409)
        except:
            return HttpResponse('Something went wrong!', status=500)


class BillView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return f'{self.url}?successUrl=alexfire.shvarev.com'

    def get(self, request, *args, **kwargs):
        try:
            amount = float(request.GET.get('amount', 1.00))
            comment = request.GET.get('comment', '')
            bill = Bill.objects.create(amount=amount, comment=comment)
            self.url = bill.get_url()

            return super(BillView, self).get(self, request, *args, **kwargs)
        except:
            return HttpResponse('Something went wrong!', status=400)
