from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import socket
import logging
import subprocess
import json
import boto3
import uuid
from datetime import datetime, timezone
from django.conf import settings
from .models import book
from .cognito_auth import CognitoAuth

logger = logging.getLogger(__name__)

def log_login_attempt(username, request, success, error_message=None):
    """Log login attempt to DynamoDB"""
    try:
        dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
        table = dynamodb.Table('UserLoginAudit')
        
        now = datetime.now(timezone.utc)
        timestamp = now.isoformat()
        login_date = now.strftime('%Y-%m-%d')
        
        # Get client info
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'unknown'))
        if ',' in ip_address:
            ip_address = ip_address.split(',')[0].strip()
        
        user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')
        
        # Create audit record
        item = {
            'user_id': username,
            'login_timestamp': timestamp,
            'login_date': login_date,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'login_successful': success,
            'session_id': str(uuid.uuid4()),
            'ttl': int((now.timestamp()) + (365 * 24 * 60 * 60))  # 1 year TTL
        }
        
        if not success and error_message:
            item['error_message'] = error_message
            
        table.put_item(Item=item)
        
    except Exception as e:
        logger.error(f'Failed to log login attempt: {str(e)}')



def login_view(request):
    if request.session.get('authenticated'):
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        cognito_auth = CognitoAuth()
        is_authenticated, result = cognito_auth.authenticate(username, password)
        
        if is_authenticated is True:
            log_login_attempt(username, request, True)
            request.session['authenticated'] = True
            request.session['username'] = username
            return redirect('home')
        elif is_authenticated == 'PASSWORD_RESET_REQUIRED':
            log_login_attempt(username, request, False, 'Password reset required')
            return render(request, 'login.html', {'error': 'Password reset required. Please contact administrator.'})
        elif is_authenticated == 'FORCE_CHANGE_PASSWORD':
            log_login_attempt(username, request, False, 'Password change required')
            return render(request, 'login.html', {'error': 'Password change required. Please contact administrator.'})
        else:
            log_login_attempt(username, request, False, str(result))
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

def about(request):
    if not request.session.get('authenticated'):
        return redirect('login')
    HostName = socket.gethostname()
    return render(request, 'about.html', {'HostName':HostName})
