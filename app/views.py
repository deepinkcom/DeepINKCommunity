from datetime import datetime

from django.http import HttpRequest
from django.shortcuts import render


def home(request):
    """Display the public homepage."""
    assert isinstance(request, HttpRequest)

    return render(
        request,
        "app/index.html",
        {
            "title": "Home",
            "year": datetime.now().year,
            "active_page": "home",
        },
    )


def about(request):
    """Display the About Us page."""
    assert isinstance(request, HttpRequest)

    return render(
        request,
        "app/about.html",
        {
            "title": "About Us",
            "year": datetime.now().year,
            "active_page": "about",
        },
    )


def programmes(request):
    """Display the programmes page."""
    assert isinstance(request, HttpRequest)

    return render(
        request,
        "app/programmes.html",
        {
            "title": "Our Programmes",
            "year": datetime.now().year,
            "active_page": "programmes",
        },
    )


def get_involved(request):
    """Display the Get Involved page."""
    assert isinstance(request, HttpRequest)

    return render(
        request,
        "app/get_involved.html",
        {
            "title": "Get Involved",
            "year": datetime.now().year,
            "active_page": "get_involved",
        },
    )


def contact(request):
    """Display the Contact page."""
    assert isinstance(request, HttpRequest)

    return render(
        request,
        "app/contact.html",
        {
            "title": "Contact",
            "year": datetime.now().year,
            "active_page": "contact",
        },
    )