from django.shortcuts import render


def index(request, *args, **kwargs):
    return render(
        request,
        'treemenu/index.html',
        context={'args': args, **kwargs}
    )
