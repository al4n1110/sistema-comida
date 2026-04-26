from django.db import models
from django.contrib.auth.models import User


# 1. USUARIO PERFIL (se enlaza 1 a 1 con User)
class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    id_usuario = models.AutoField(primary_key=True)
    ci = models.CharField(max_length=20, unique=True, blank=True, null=True)
    nombres = models.CharField(max_length=50, blank=True)
    paterno = models.CharField(max_length=50, blank=True)
    materno = models.CharField(max_length=50, blank=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)

    TIPO_CHOICES = (
        ('admin', 'Administrador'),
        ('cliente', 'Cliente'),
        ('repartidor', 'Repartidor'),
    )
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_CHOICES)

    def __str__(self):
        return f"{self.nombres} {self.paterno} ({self.tipo_usuario})"


# 2. CLIENTE
class Cliente(models.Model):
    # clave primaria es el mismo Usuario
    id_cliente = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    direccion = models.CharField(max_length=200, blank=True)
    preferencias_entrega = models.CharField(max_length=200, blank=True)
    fecha_registro = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Cliente: {self.id_cliente.nombres} {self.id_cliente.paterno}"


# 3. REPARTIDOR
class Repartidor(models.Model):
    # clave primaria es el mismo Usuario
    id_repartidor = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    sueldo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vehiculo = models.CharField(max_length=30, blank=True)
    tipo_vehiculo = models.CharField(max_length=50, blank=True)
    disponibilidad = models.BooleanField(default=True)

    def __str__(self):
        return f"Repartidor: {self.id_repartidor.nombres} {self.id_repartidor.paterno}"


# 4. EMPRESA
class Empresa(models.Model):
    id_empresa = models.AutoField(primary_key=True)
    nit = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField()
    
    logo = models.ImageField(upload_to="empresas/", blank=True, null=True)

    def __str__(self):
        return self.nombre


# 5. SUCURSAL
class Sucursal(models.Model):
    id_sucursal = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)  # para usar sucursal.nombre en templates
    direccion = models.CharField(max_length=200)
    horario_apertura = models.TimeField()
    horario_cierre = models.TimeField()
    telefono = models.CharField(max_length=20)
    
    imagen = models.ImageField(upload_to="sucursales/", blank=True, null=True)

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="sucursales")

    # N:M — Una sucursal puede ofrecer muchos platos y un plato puede estar en varias sucursales
    platos = models.ManyToManyField('Plato', related_name="sucursales", blank=True)

    def __str__(self):
        return f"{self.id_sucursal} {self.nombre} ({self.empresa.nombre})"


# 6. PLATO
class Plato(models.Model):
    id_plato = models.AutoField(primary_key=True)
    nombre_plato = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=50)
    disponibilidad = models.BooleanField(default=True)
    
    imagen = models.ImageField(upload_to="platos/", blank=True, null=True)

    def __str__(self):
        return self.nombre_plato


# 7. PEDIDO
class Pedido(models.Model):
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('asignado', 'Asignado'),
        ('entregado', 'Entregado'),
    )

    id_pedido = models.AutoField(primary_key=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="pendiente")
    precio_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    direccion_entrega = models.CharField(max_length=200)

    # RELACIONES
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="pedidos")
    repartidor = models.ForeignKey(Repartidor, on_delete=models.SET_NULL, null=True, blank=True)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)

    def __str__(self):
        return f"Pedido #{self.id_pedido} - {self.cliente.id_cliente.nombres}"


# 8. DETALLE DEL PEDIDO
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="detalles")
    plato = models.ForeignKey(Plato, on_delete=models.CASCADE)

    fecha_pedido = models.DateField(auto_now_add=True)
    hora_pedido = models.TimeField(auto_now_add=True)

    cantidad = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.plato.nombre_plato} (Pedido #{self.pedido.id_pedido})"
