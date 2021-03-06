import json
import requests

from django.db import models


class Bill(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    bill_id = models.IntegerField(null=True, blank=True)
    comment = models.CharField(max_length=45, default='')
    amount = models.FloatField(default=1.00)
    status = models.CharField(max_length=15, null=True, blank=True)

    def get_url(self):
        try:
            url = "https://oplata.alexfire.shvarev.com/create/"

            headers = {
                'Content-Type': 'application/json',
            }

            request_data = {
                'comment': f'{self.comment}',
                'amount': round(self.amount, 2),
                'site': 'https://alexfire.shvarev.com/billing/succcess/'
            }

            response = requests.request('POST', url, data=json.dumps(request_data), headers=headers)
            data = response.json()
            self.status = 'WAITING'
            self.bill_id = data['id']
            return data['payUrl']
        except:
            return None

    def success(self):
        self.status = 'SUCCESS'
