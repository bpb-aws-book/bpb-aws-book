from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
import socket
import boto3
from .models import book


def home(request):
    books = book.objects.filter(is_rented=False)
    rentedbooks = book.objects.filter(is_rented=True)
    return render(request, 'home.html', {'books':books, 'rentedbooks':rentedbooks})



def details(request, pk):
    try:
        s3_client = boto3.client('s3')
        s3_response_object = s3_client.get_object(Bucket="BPBS3Bucket", Key="samplechapter.pdf")
        object_content = s3_response_object['Body'].read()
        response = HttpResponse(object_content, content_type='application/pdf')
        print(response)
    except Exception as e:
            print(f"Error occurred: {str(e)}")
    TheBook = book.objects.get(pk=pk)
        
        #response = FileResponse(open("/Users/shkhars/Shashi/EBook/chapter9/inquisitive_bookworm_club/aaaa.pdf", "rb"), "")
    if TheBook:
            return render(request,"details.html",{'book':TheBook, 'pdfdoc':response}) 
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

def displaysamplechapter(request, pk):
    try:
        print("PRINTING VALUE")
        print(pk)
        s3_client = boto3.client('s3')
        s3_response_object = s3_client.get_object(Bucket="BPBS3Bucket", Key="samplechapter.pdf")
        object_content = s3_response_object['Body'].read()
        response = HttpResponse(object_content, content_type='application/pdf')
    except Exception as e:
        print(f"Error occurred: {str(e)}")    
    
    return response if response else HttpResponse("Error retrieving PDF")

def about(request):
    HostName = socket.gethostname()
    return render(request, 'about.html', {'HostName':HostName})
