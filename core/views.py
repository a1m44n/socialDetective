from django.http import HttpResponse

def home(request):
    return HttpResponse("Hello, SocialDetective is Live! 🚀")
