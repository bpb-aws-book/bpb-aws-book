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
            request.session['reset_session'] = result
            request.session['reset_username'] = username
            return redirect('password_reset')
        elif is_authenticated == 'FORCE_CHANGE_PASSWORD':
            request.session['force_reset_username'] = result
            return redirect('force_password_reset')
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

def password_reset_view(request):
    if not request.session.get('reset_session'):
        return redirect('login')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        username = request.session.get('reset_username')
        session = request.session.get('reset_session')
        
        cognito_auth = CognitoAuth()
        success, result = cognito_auth.reset_password(username, new_password, session)
        
        if success:
            request.session['authenticated'] = True
            request.session['username'] = username
            del request.session['reset_session']
            del request.session['reset_username']
            return redirect('home')
        else:
            return render(request, 'password_reset.html', {'error': f'Password reset failed: {result}'})
    
    return render(request, 'password_reset.html')

def force_password_reset_view(request):
    if not request.session.get('force_reset_username'):
        return redirect('login')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        username = request.session.get('force_reset_username')
        
        cognito_auth = CognitoAuth()
        success, result = cognito_auth.admin_set_permanent_password(username, new_password)
        
        if success:
            request.session['authenticated'] = True
            request.session['username'] = username
            del request.session['force_reset_username']
            return redirect('home')
        else:
            return render(request, 'force_password_reset.html', {'error': f'Password reset failed: {result}'})
    
    return render(request, 'force_password_reset.html')

def about(request):
    if not request.session.get('authenticated'):
        return redirect('login')
    HostName = socket.gethostname()
    return render(request, 'about.html', {'HostName':HostName})

def api_test(request):
    if not request.session.get('authenticated'):
        return redirect('login')
    
    context = {}
    
    if request.method == 'POST':
        api_url = request.POST.get('api_url')
        jwt_token = request.POST.get('jwt_token')
        
        # Create curl command
        curl_command = f'curl -X GET "{api_url}" -H "Authorization: Bearer {jwt_token}"'
        
        try:
            # Execute curl command
            result = subprocess.run(
                ['curl', '-X', 'GET', api_url, '-H', f'Authorization: Bearer {jwt_token}'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                try:
                    # Try to format JSON response
                    json_response = json.loads(result.stdout)
                    api_result = json.dumps(json_response, indent=2)
                except json.JSONDecodeError:
                    api_result = result.stdout
            else:
                api_result = f"Error: {result.stderr}"
            
            context.update({
                'api_url': api_url,
                'jwt_token': jwt_token,
                'api_result': api_result,
                'curl_command': curl_command
            })
            
        except subprocess.TimeoutExpired:
            context.update({
                'api_url': api_url,
                'jwt_token': jwt_token,
                'error': 'Request timed out after 30 seconds',
                'curl_command': curl_command
            })
        except Exception as e:
            context.update({
                'api_url': api_url,
                'jwt_token': jwt_token,
                'error': str(e),
                'curl_command': curl_command
            })
    
    return render(request, 'api_test.html', context)
