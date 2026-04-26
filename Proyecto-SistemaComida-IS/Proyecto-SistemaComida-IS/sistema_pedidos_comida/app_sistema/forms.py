from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Usuario, Cliente, Repartidor, Empresa, Sucursal, Plato, Pedido, DetallePedido

class RegistroForm(UserCreationForm):
    TIPO_CHOICES = (
        ('admin', 'Administrador'),
        ('cliente', 'Cliente'),
        ('repartidor', 'Repartidor'),
    )
    tipo_usuario = forms.ChoiceField(choices=TIPO_CHOICES, label="Tipo de usuario")
    email = forms.EmailField(required=True)
    first_name = forms.CharField(label='Nombre', max_length=50, required=True)
    last_name = forms.CharField(label='Apellido', max_length=50, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'tipo_usuario']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()

            tipo = self.cleaned_data['tipo_usuario']
            usuario = Usuario.objects.create(
                user=user,
                nombres=user.first_name,
                paterno=user.last_name,
                email=user.email,
                tipo_usuario=tipo,
            )

            if tipo == 'cliente':
                Cliente.objects.create(id_cliente=usuario)
            elif tipo == 'repartidor':
                Repartidor.objects.create(id_repartidor=usuario)

        return user


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['direccion', 'preferencias_entrega']
        widgets = {
            'preferencias_entrega': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
        }


class RepartidorForm(forms.ModelForm):
    class Meta:
        model = Repartidor
        fields = ['sueldo', 'vehiculo', 'tipo_vehiculo', 'disponibilidad']
        widgets = {
            'sueldo': forms.NumberInput(attrs={'class': 'form-control'}),
            'vehiculo': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_vehiculo': forms.TextInput(attrs={'class': 'form-control'}),
            'disponibilidad': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nit', 'nombre', 'telefono', 'correo', 'logo']
        widgets = {
            'nit': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class SucursalForm(forms.ModelForm):
    class Meta:
        model = Sucursal
        fields = ['nombre', 'direccion', 'horario_apertura', 'horario_cierre', 'telefono', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'horario_apertura': forms.TimeInput(attrs={'class': 'form-control'}),
            'horario_cierre': forms.TimeInput(attrs={'class': 'form-control'}),
        }


class PlatoForm(forms.ModelForm):
    class Meta:
        model = Plato
        fields = ['nombre_plato', 'descripcion', 'precio', 'categoria', 'disponibilidad', 'imagen']
        widgets = {
            'nombre_plato': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control'}),
            'disponibilidad': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


# AHORA el pedido sólo pide la dirección; todo lo demás se rellena en la vista
class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['direccion_entrega']
        widgets = {
            'direccion_entrega': forms.TextInput(attrs={'class': 'form-control'}),
        }


from .models import DetallePedido, Plato

class DetallePedidoForm(forms.ModelForm):
    class Meta:
        model = DetallePedido
        fields = ['plato', 'cantidad']
        widgets = {
            'plato': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

    def __init__(self, *args, **kwargs):
        pedido = kwargs.pop('pedido', None)
        super().__init__(*args, **kwargs)

        if pedido is not None:
            # Sólo platos de la sucursal del pedido y disponibles
            self.fields['plato'].queryset = Plato.objects.filter(
                sucursales=pedido.sucursal,
                disponibilidad=True
            ).distinct()

