from django.shortcuts import render


def passview(request):
    return render(request, 'pass.html')
