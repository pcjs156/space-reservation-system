from django.shortcuts import render


def main_view(request, *args, **kwargs):
    context = {
        'toastType': kwargs.get('toastType')
    }
    return render(request, 'commons/main.html', context)


def handler_404_view(request, *args, **kwargs):
    return render(request, 'commons/errors/404.html')


def handler_500_view(request, *args, **kwargs):
    return render(request, 'commons/errors/500.html')
