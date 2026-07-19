from django import forms


class RegistroForm(forms.Form):

    nombre = forms.CharField(
        label='Nombre completo',
        max_length=100
    )

    correo = forms.EmailField(
        label='Correo electrónico',
        max_length=100
    )

    contrasena = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput
    )

    confirmar_contrasena = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput
    )

    def clean(self):
        datos_limpios = super().clean()
        contrasena = datos_limpios.get('contrasena')
        confirmar_contrasena = datos_limpios.get('confirmar_contrasena')

        if contrasena and confirmar_contrasena and contrasena != confirmar_contrasena:
            self.add_error('confirmar_contrasena', 'Las contraseñas no coinciden')

        return datos_limpios


class LoginForm(forms.Form):

    correo = forms.EmailField(
        label='Correo electrónico'
    )

    contrasena = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput
    )
