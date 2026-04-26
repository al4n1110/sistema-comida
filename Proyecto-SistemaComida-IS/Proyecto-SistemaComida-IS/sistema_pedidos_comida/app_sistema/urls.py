from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.salir, name='salir'),
    path('registrar/', views.registrar, name='registrar'),

    path('empresas/', views.lista_empresas, name='lista_empresas'),
    path('empresas/crear/', views.crear_empresa, name='crear_empresa'),
    path('empresas/<int:empresa_id>/sucursales/', views.lista_sucursales, name='lista_sucursales'),
    path('empresas/<int:empresa_id>/sucursales/crear/', views.crear_sucursal, name='crear_sucursal'),

    path('sucursal/<int:sucursal_id>/platos/', views.platos_sucursal, name='platos_sucursal'),
    path('sucursal/<int:sucursal_id>/pedidos/crear/', views.crear_pedido, name='crear_pedido'),

    path('pedidos/<int:pedido_id>/agregar-detalle/', views.agregar_detalle, name='agregar_detalle'),
    path('pedidos/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),

    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('sucursal/<int:sucursal_id>/platos/crear/', views.crear_plato, name='crear_plato'),
    
    path('repartidor/pedidos-pendientes/', views.pedidos_pendientes_repartidor, name='pedidos_pendientes'),
    path('repartidor/pedidos/<int:pedido_id>/tomar/', views.tomar_pedido, name='tomar_pedido'),

    # PANEL ADMIN
    path('panel/pedidos/', views.lista_pedidos_admin, name='lista_pedidos_admin'),
    path('panel/clientes/', views.lista_clientes_admin, name='lista_clientes_admin'),
    path('panel/repartidores/', views.lista_repartidores_admin, name='lista_repartidores_admin'),

    # CRUD Empresa
    path('empresas/<int:empresa_id>/editar/', views.editar_empresa, name='editar_empresa'),
    path('empresas/<int:empresa_id>/eliminar/', views.eliminar_empresa, name='eliminar_empresa'),

    # CRUD Sucursal
    path('sucursales/<int:sucursal_id>/editar/', views.editar_sucursal, name='editar_sucursal'),
    path('sucursales/<int:sucursal_id>/eliminar/', views.eliminar_sucursal, name='eliminar_sucursal'),

    # CRUD Plato
    path('platos/<int:plato_id>/editar/', views.editar_plato, name='editar_plato'),
    path('platos/<int:plato_id>/eliminar/', views.eliminar_plato, name='eliminar_plato'),
    
    path('cliente/completar-perfil/', views.completar_cliente, name='completar_cliente'),
    path('repartidor/completar-perfil/', views.completar_repartidor, name='completar_repartidor'),
    
    path('pedidos/<int:pedido_id>/confirmar-entrega/', views.confirmar_entrega, name='confirmar_entrega'),

]

