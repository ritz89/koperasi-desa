from django import forms

from commerce.models import Delivery, Address, UserProfile


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


class ProfileForm(forms.ModelForm):
    fullname = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Nama Lengkap'
            }
        )
    )
    no_hp = forms.CharField(
        max_length=15,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'No Hp'
            }
        )
    )

    profile_picture = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'form-control'
            }
        ),
        required=False
    )

    class Meta:
        model = UserProfile
        fields = ['fullname', 'no_hp', 'profile_picture']

