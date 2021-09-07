from django.shortcuts import render, redirect

# Create your views here.
def index(request):
    return render(request, 'generator/index.html')


def generate_citation_text(request):
    print(request.POST.get('citing_context'))
    return redirect('/')