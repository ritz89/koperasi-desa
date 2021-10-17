from django import forms

from commerce.models import Delivery, Address


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = '__all__'


class AddressFormDusun(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address', 'dusun', 'latitude', 'longitude']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'dusun': forms.Select(attrs={'class': 'form-control'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput()
        }

    def clean(self):
        cleaned_data = super().clean()
        dusun = cleaned_data.get("dusun")
        latitude = cleaned_data.get("latitude")

        if dusun is None and latitude is None:
            msg = "salah satu dari dusun atau lokaso harus terisi. silahkan pikih lokasi di peta untuk " \
                  "pengiriman luar desa"
            self.add_error('dusun', msg)
            self.add_error('latitude', msg)

