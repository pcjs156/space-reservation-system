from django.shortcuts import render
from django.views import View


def main_view(request, *args, **kwargs):
    context = {
        'toastType': kwargs.get('toastType')
    }
    return render(request, 'commons/main.html', context)


def handler_404_view(request, *args, **kwargs):
    return render(request, 'commons/errors/404.html')


def handler_500_view(request, *args, **kwargs):
    return render(request, 'commons/errors/500.html')


class ViewWithContext(View):
    def __init__(self, *args, **kwargs):
        super(ViewWithContext, self).__init__(*args, **kwargs)
        self.context = dict()
