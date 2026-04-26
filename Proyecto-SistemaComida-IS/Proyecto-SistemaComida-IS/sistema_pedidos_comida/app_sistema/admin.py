from django.contrib import admin
from .models import Usuario, Cliente, Repartidor, Empresa, Sucursal, Plato, Pedido, DetallePedido 
# Register your models here.

admin.site.register(Usuario)
admin.site.register(Cliente)
admin.site.register(Repartidor)
admin.site.register(Empresa)
admin.site.register(Sucursal)
admin.site.register(Plato)
admin.site.register(Pedido)
admin.site.register(DetallePedido)

