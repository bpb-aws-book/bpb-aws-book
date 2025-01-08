from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
import socket
from .models import book
import boto3


def home(request):
    books = book.objects.filter(is_rented=False)
    rentedbooks = book.objects.filter(is_rented=True)
    return render(request, 'home.html', {'books':books, 'rentedbooks':rentedbooks})

def details(request, pk):
    TheBook = book.objects.get(pk=pk)
    if TheBook:
        return render(request,"details.html",{'book':TheBook}) 
    else:
        return HttpResponse("Book not found")

def rentbook(request, pk):
    TheBook =  book.objects.get(pk=pk)
    if TheBook:
        TheBook.is_rented = True
        TheBook.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponse("Book not found")

def returnbook(request, pk):
    TheBook =  book.objects.get(pk=pk)
    if TheBook:
        TheBook.is_rented = False
        TheBook.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponse("Book not found")

def about(request):
    HostName = socket.gethostname()
    return render(request, 'about.html', {'HostName':HostName})

def displaysamplechapter(request, pk):
    try:
        s3_client = boto3.client('s3')
        s3_response_object = s3_client.get_object(Bucket="BPBS3Bucket", Key="samplechapter.pdf")
        object_content = s3_response_object['Body'].read()
        response = HttpResponse(object_content, content_type='application/pdf')
        return response
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return HttpResponse(str(e))    
