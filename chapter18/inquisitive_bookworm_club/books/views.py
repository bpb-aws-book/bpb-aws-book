from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import socket
import logging
import subprocess
import json
from .models import book
from .cognito_auth import CognitoAuth

logger = logging.getLogger(__name__)


def login_view(request):
    if request.session.get('authenticated'):
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        cognito_auth = CognitoAuth()
        is_authenticated, result = cognito_auth.authenticate(username, password)
        
        if is_authenticated is True:
            request.session['authenticated'] = True
            request.session['username'] = username
            return redirect('home')
        elif is_authenticated == 'PASSWORD_RESET_REQUIRED':
            # Password reset disabled - redirect to login with error
            return render(request, 'login.html', {'error': 'Password reset required. Please contact administrator.'})
        elif is_authenticated == 'FORCE_CHANGE_PASSWORD':
            # Force password reset disabled - redirect to login with error
            return render(request, 'login.html', {'error': 'Password change required. Please contact administrator.'})
        else:
            logger.error(f'Authentication failed for user {username}: {result}')
            return render(request, 'login.html', {'error': f'Authentication failed: {result}'})
    
    return render(request, 'login.html')

def logout_view(request):
    request.session.flush()
    return redirect('login')

def home(request):
    if not request.session.get('authenticated'):
        return redirect('login')
    books = book.objects.filter(is_rented=False)
    rentedbooks = book.objects.filter(is_rented=True)
    return render(request, 'home.html', {'books':books, 'rentedbooks':rentedbooks})

def details(request, pk):
    if not request.session.get('authenticated'):
        return redirect('login')
    TheBook = book.objects.get(pk=pk)
    if TheBook:
        return render(request,"details.html",{'book':TheBook}) 
    else:
        return HttpResponse("Book not found")

def rentbook(request, pk):
    if not request.session.get('authenticated'):
        return redirect('login')
    TheBook =  book.objects.get(pk=pk)
    if TheBook:
        TheBook.is_rented = True
        TheBook.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponse("Book not found")

def returnbook(request, pk):
    if not request.session.get('authenticated'):
        return redirect('login')
    TheBook =  book.objects.get(pk=pk)
    if TheBook:
        TheBook.is_rented = False
        TheBook.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponse("Book not found")

# def password_reset_view(request):
#     # Password reset functionality disabled
#     return redirect('login')

# def force_password_reset_view(request):
#     # Force password reset functionality disabled
#     return redirect('login')

def about(request):
    if not request.session.get('authenticated'):
        return redirect('login')
    HostName = socket.gethostname()
    return render(request, 'about.html', {'HostName':HostName})

# def api_test(request):
#     # API test functionality disabled
#     return redirect('home')
