from django.shortcuts import render, redirect
from django.http import HttpResponse

# Create your views here.
def index(request):
    return render(request, 'index.html')


def generate_citation_text(request):
    print(request.POST.get('citing_input_type'))
    return render(request, 'feedback.html')