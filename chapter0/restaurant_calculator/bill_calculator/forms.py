from django import forms

class BillCalculatorForm(forms.Form):
    billamount = forms.DecimalField(label='Bill Amount', decimal_places=2)
    taxrate = forms.DecimalField(label='Tax Rate', decimal_places=2)