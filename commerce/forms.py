from django import forms

from commerce.models import Delivery


class DeliveryForm(forms.ModelForm):

    class Meta:
        model = Delivery
        fields = '__all__'

