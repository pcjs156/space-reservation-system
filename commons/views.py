from django.shortcuts import render


def main_view(request, *args, **kwargs):
    context = {
        'toastType': kwargs.get('toastType')
    }
    return render(request, 'commons/main.html', context)
