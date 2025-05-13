from django.shortcuts import render
from .forms import BillCalculatorForm

def calculate_bill(bill_amount, tax_rate):
    """Calculate the final bill amount with tax."""
    return bill_amount + (bill_amount * tax_rate / 100)

def index(request):
    result = None
    
    if request.method == 'POST':
        form = BillCalculatorForm(request.POST)
        if form.is_valid():
            bill_amount = form.cleaned_data['billamount']
            tax_rate = form.cleaned_data['taxrate']
            final_bill = calculate_bill(bill_amount, tax_rate)
            
            result = {
                'bill_amount': bill_amount,
                'tax_rate': tax_rate,
                'final_bill': final_bill
            }
    else:
        form = BillCalculatorForm()
    
    return render(request, 'bill_calculator/index.html', {
        'form': form,
        'result': result
    })