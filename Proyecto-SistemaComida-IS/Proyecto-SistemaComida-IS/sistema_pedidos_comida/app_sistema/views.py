from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse


from .forms import (
    RegistroForm, PedidoForm, DetallePedidoForm, EmpresaForm,
    SucursalForm, PlatoForm, ClienteForm, RepartidorForm
)
from .models import Empresa, Sucursal, Plato, Pedido, DetallePedido, Usuario, Cliente, Repartidor


def _get_tipo_usuario(request):
    if not request.user.is_authenticated:
        return None
    try:
        return request.user.usuario.tipo_usuario
    except Usuario.DoesNotExist:
        return None


def home(request):
    tipo = _get_tipo_usuario(request)
    return render(request, 'app_sistema/home.html', {'tipo_usuario': tipo})


def salir(request):
    logout(request)
    return redirect('home')

def registrar(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()  
            tipo = form.cleaned_data['tipo_usuario']

            # Crear o recuperar Usuario asociado a este User
            usuario, created = Usuario.objects.get_or_create(
                user=user,
                defaults={
                    "tipo_usuario": tipo,
                    "nombres": form.cleaned_data['first_name'],
                    "paterno": form.cleaned_data['last_name'],
                    "email": form.cleaned_data['email'],
                },
            )

            # Si ya existía, actualizamos por si cambia algo
            if not created:
                usuario.tipo_usuario = tipo
                usuario.nombres = form.cleaned_data['first_name']
                usuario.paterno = form.cleaned_data['last_name']
                usuario.email = form.cleaned_data['email']
                usuario.save()

            login(request, user)

            if tipo == 'cliente':
                Cliente.objects.get_or_create(
                    id_cliente=usuario,
                    defaults={
                        "direccion": "",
                        "preferencias_entrega": "",
                    }
                )
                messages.success(request, "Registro exitoso. Completa tus datos de cliente.")
                return redirect('completar_cliente')

            elif tipo == 'repartidor':
                Repartidor.objects.get_or_create(
                    id_repartidor=usuario,
                    defaults={
                        "sueldo": 0,
                        "vehiculo": "",
                        "tipo_vehiculo": "",
                        "disponibilidad": True,
                    }
                )
                messages.success(request, "Registro exitoso. Completa tus datos de repartidor.")
                return redirect('completar_repartidor')

            else:  # admin
                messages.success(request, "Registro exitoso como administrador.")
                return redirect("home")
    else:
        form = RegistroForm()

    return render(request, 'registro/registrar.html', {"form": form})


def iniciar_sesion(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Credenciales inválidas.")
    else:
        form = AuthenticationForm()
    return render(request, 'registro/login.html', {'form': form})


@login_required
def lista_empresas(request):
    empresas = Empresa.objects.all()
    tipo = _get_tipo_usuario(request)   

    return render(
        request,
        "app_sistema/lista_empresas.html",
        {
            "empresas": empresas,
            "tipo_usuario": tipo,       
        }
    )



@login_required
def lista_sucursales(request, empresa_id):
    empresa = get_object_or_404(Empresa, pk=empresa_id)
    sucursales = Sucursal.objects.filter(empresa=empresa)
    tipo = _get_tipo_usuario(request)

    return render(request, "app_sistema/lista_sucursales.html", {
        "empresa": empresa,
        "sucursales": sucursales,
        "tipo_usuario": tipo,
    })



@login_required
def platos_sucursal(request, sucursal_id):
    sucursal = get_object_or_404(Sucursal, pk=sucursal_id)
    platos = sucursal.platos.all()
    tipo = _get_tipo_usuario(request)

    return render(request, "app_sistema/platos_sucursal.html", {
        "sucursal": sucursal,
        "platos": platos,
        "tipo_usuario": tipo,
    })



@login_required
def crear_pedido(request, sucursal_id):
    # Solo CLIENTE puede crear pedidos
    tipo = _get_tipo_usuario(request)
    if tipo != 'cliente':
        return HttpResponseForbidden("Solo un cliente puede hacer pedidos.")

    sucursal = get_object_or_404(Sucursal, pk=sucursal_id)
    usuario = get_object_or_404(Usuario, user=request.user)
    cliente = get_object_or_404(Cliente, id_cliente=usuario)

    if request.method == "POST":
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.cliente = cliente
            pedido.sucursal = sucursal
            pedido.estado = "pendiente"
            pedido.precio_total = 0
            pedido.save()
            return redirect("agregar_detalle", pedido_id=pedido.id_pedido)
    else:
        form = PedidoForm()

    return render(request, "app_sistema/crear_pedido.html", {
        "form": form,
        "sucursal": sucursal
    })


@login_required
def agregar_detalle(request, pedido_id):
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id)

    if request.method == "POST":
        form = DetallePedidoForm(request.POST, pedido=pedido)
        if form.is_valid():
            detalle = form.save(commit=False)
            detalle.pedido = pedido
            detalle.subtotal = detalle.cantidad * detalle.plato.precio
            detalle.save()

            pedido.precio_total += detalle.subtotal
            pedido.save()

            return redirect('agregar_detalle', pedido_id=pedido.id_pedido)
    else:
        form = DetallePedidoForm(pedido=pedido)

    return render(request, "app_sistema/agregar_detalle.html", {
        "form": form,
        "pedido": pedido
    })


@login_required
def mis_pedidos(request):
    usuario = get_object_or_404(Usuario, user=request.user, tipo_usuario='cliente')
    cliente = get_object_or_404(Cliente, id_cliente=usuario)

    pedidos = Pedido.objects.filter(
        cliente=cliente
    ).select_related('sucursal').order_by('-id_pedido')

    return render(request, "app_sistema/mis_pedidos.html", {"pedidos": pedidos})



@login_required
def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    detalles = pedido.detalles.all()
    total = sum(d.subtotal for d in detalles)

    cliente = pedido.cliente  

    return render(request, "app_sistema/detalle_pedido.html", {
        "pedido": pedido,
        "detalles": detalles,
        "total": total,
        "cliente": cliente,
    })



# -------- VISTAS SOLO ADMIN --------

@login_required
def crear_empresa(request):
    if _get_tipo_usuario(request) != 'admin':
        return HttpResponseForbidden("No tienes permiso para crear empresas.")

    if request.method == "POST":
        form = EmpresaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("lista_empresas")
    else:
        form = EmpresaForm()

    return render(request, "app_sistema/crear_empresa.html", {"form": form})


@login_required
def crear_sucursal(request, empresa_id):
    if _get_tipo_usuario(request) != 'admin':
        return HttpResponseForbidden("No tienes permiso para crear sucursales.")

    empresa = get_object_or_404(Empresa, pk=empresa_id)

    if request.method == "POST":
        form = SucursalForm(request.POST, request.FILES)
        if form.is_valid():
            sucursal = form.save(commit=False)
            sucursal.empresa = empresa
            sucursal.save()
            form.save_m2m()
            return redirect("lista_sucursales", empresa_id=empresa.id_empresa)
    else:
        form = SucursalForm()

    return render(request, "app_sistema/crear_sucursal.html", {"form": form, "empresa": empresa})


@login_required
def crear_plato(request, sucursal_id):
    if _get_tipo_usuario(request) != 'admin':
        return HttpResponseForbidden("No tienes permiso para crear platos.")

    sucursal = get_object_or_404(Sucursal, pk=sucursal_id)

    if request.method == "POST":
        form = PlatoForm(request.POST, request.FILES)
        if form.is_valid():
            plato = form.save()
            sucursal.platos.add(plato)
            return redirect("platos_sucursal", sucursal_id=sucursal.id_sucursal)
    else:
        form = PlatoForm()

    return render(request, "app_sistema/crear_plato.html", {
        "form": form,
        "sucursal": sucursal,
    })



# -------- VISTA REPARTIDOR -------
@login_required
def pedidos_pendientes_repartidor(request):
    # Solo repartidores
    usuario = get_object_or_404(Usuario, user=request.user, tipo_usuario='repartidor')
    repartidor = get_object_or_404(Repartidor, id_repartidor=usuario)

    # Pedidos que el repartidor puede ver:
    # pendientes y aún sin repartidor o asignados a él
    pedidos = Pedido.objects.filter(
        Q(estado='pendiente', repartidor__isnull=True) |
        Q(estado='asignado', repartidor=repartidor)
    ).select_related('cliente__id_cliente', 'sucursal').order_by('-id_pedido')  

    return render(
        request,
        "app_sistema/pedidos_pendientes_repartidor.html",
        {"pedidos": pedidos}
    )




@login_required
def tomar_pedido(request, pedido_id):
    if _get_tipo_usuario(request) != 'repartidor':
        return HttpResponseForbidden("Solo repartidores pueden tomar pedidos.")

    usuario = get_object_or_404(Usuario, user=request.user)
    repartidor = get_object_or_404(Repartidor, id_repartidor=usuario)

    pedido = get_object_or_404(Pedido, pk=pedido_id)

    # Solo permitir tomarlo si sigue libre y pendiente
    if pedido.repartidor is None and pedido.estado == 'pendiente':
        pedido.repartidor = repartidor
        pedido.estado = 'asignado'
        pedido.save()

    return redirect('pedidos_pendientes')

@login_required
def lista_pedidos_admin(request):
    if _get_tipo_usuario(request) != 'admin':
        return HttpResponseForbidden("Solo administradores pueden ver esta página.")

    pedidos = Pedido.objects.select_related(
        'cliente', 'repartidor', 'sucursal'
    ).order_by('-id_pedido')   

    return render(
        request,
        "app_sistema/lista_pedidos_admin.html",
        {"pedidos": pedidos}
    )


#  VISTAS ADMIN: LISTAS
@login_required
def lista_clientes_admin(request):
    if _get_tipo_usuario(request) != 'admin':
        return HttpResponseForbidden("Solo administradores pueden ver esta página.")

    clientes = Cliente.objects.select_related('id_cliente__user').order_by('id_cliente__nombres')
    return render(request, "app_sistema/lista_clientes_admin.html", {"clientes": clientes})


@login_required
def lista_repartidores_admin(request):
    if _get_tipo_usuario(request) != 'admin':
        return HttpResponseForbidden("Solo administradores pueden ver esta página.")

    repartidores = Repartidor.objects.select_related('id_repartidor__user').order_by('id_repartidor__nombres')
    return render(request, "app_sistema/lista_repartidores_admin.html", {"repartidores": repartidores})

# VISTAS ADMIN: EDITAR Y ELIMINAR EMPRESA
@login_required
def editar_empresa(request, empresa_id):
    if _get_tipo_usuario(request) != 'admin':
        return HttpResponseForbidden("Solo administradores pueden editar empresas.")

    empresa = get_object_or_404(Empresa, pk=empresa_id)

    if request.method == "POST":
        form = EmpresaForm(request.POST, request.FILES, instance=empresa)
        if form.is_valid():
            form.save()
            return redirect('lista_empresas')
    else:
        form = EmpresaForm(instance=empresa)

    return render(request, "app_sistema/editar_empresa.html", {
        "form": form,
        "empresa": empresa,
    })

@login_required
def eliminar_empresa(request, empresa_id):
    if _get_tipo_usuario(request) != 'admin':
        return HttpResponseForbidden("Solo administradores pueden eliminar empresas.")

    empresa = get_object_or_404(Empresa, pk=empresa_id)

    if request.method == "POST":
        empresa.delete()
        return redirect('lista_empresas')

    cancel_url = reverse('lista_empresas')

    return render(request, "app_sistema/confirmar_eliminacion.html", {
        "objeto": empresa,
        "tipo": "empresa",
        "cancel_url": cancel_url,
    })


# VISTAS ADMIN: EDITAR Y ELIMINAR SUCURSAL
@login_required
def editar_sucursal(request, sucursal_id):
    if _get_tipo_usuario(request) != 'admin':
        return HttpResponseForbidden("Solo administradores pueden editar sucursales.")

    sucursal = get_object_or_404(Sucursal, pk=sucursal_id)

    if request.method == "POST":
        form = SucursalForm(request.POST, request.FILES, instance=sucursal)
        if form.is_valid():
            form.save()
            return redirect("lista_sucursales", empresa_id=sucursal.empresa.id_empresa)
    else:
        form = SucursalForm(instance=sucursal)

    return render(request, "app_sistema/editar_sucursal.html", {
        "form": form,
        "sucursal": sucursal,
    })

@login_required
def eliminar_sucursal(request, sucursal_id):
    if _get_tipo_usuario(request) != 'admin':
        return HttpResponseForbidden("Solo administradores pueden eliminar sucursales.")

    sucursal = get_object_or_404(Sucursal, pk=sucursal_id)
    empresa_id = sucursal.empresa.id_empresa

    if request.method == "POST":
        sucursal.delete()
        return redirect("lista_sucursales", empresa_id=empresa_id)

    cancel_url = reverse("lista_sucursales", args=[empresa_id])

    return render(request, "app_sistema/confirmar_eliminacion.html", {
        "objeto": sucursal,
        "tipo": "sucursal",
        "cancel_url": cancel_url,
    })


# VISTAS ADMIN: EDITAR Y ELIMINAR PLATO
@login_required
def editar_plato(request, plato_id):
    if _get_tipo_usuario(request) != 'admin':
        return HttpResponseForbidden("Solo administradores pueden editar platos.")

    plato = get_object_or_404(Plato, pk=plato_id)

    sucursal = plato.sucursales.first()

    if request.method == "POST":
        form = PlatoForm(request.POST, request.FILES, instance=plato)
        if form.is_valid():
            form.save()
            if sucursal:
                return redirect("platos_sucursal", sucursal_id=sucursal.id_sucursal)
            return redirect("lista_empresas")
    else:
        form = PlatoForm(instance=plato)

    return render(request, "app_sistema/editar_plato.html", {
        "form": form,
        "plato": plato,
        "sucursal": sucursal,
    })

@login_required
def eliminar_plato(request, plato_id):
    if _get_tipo_usuario(request) != 'admin':
        return HttpResponseForbidden("Solo administradores pueden eliminar platos.")

    plato = get_object_or_404(Plato, pk=plato_id)
    sucursal = plato.sucursales.first()

    if request.method == "POST":
        plato.delete()
        if sucursal:
            return redirect("platos_sucursal", sucursal_id=sucursal.id_sucursal)
        return redirect("lista_empresas")

    if sucursal:
        cancel_url = reverse("platos_sucursal", args=[sucursal.id_sucursal])
    else:
        cancel_url = reverse("lista_empresas")

    return render(request, "app_sistema/confirmar_eliminacion.html", {
        "objeto": plato,
        "tipo": "plato",
        "cancel_url": cancel_url,
    })


@login_required
def completar_cliente(request):
    # solo clientes
    usuario = get_object_or_404(Usuario, user=request.user, tipo_usuario='cliente')
    cliente, created = Cliente.objects.get_or_create(id_cliente=usuario)

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        telefono = request.POST.get("telefono", "").strip()

        if form.is_valid():
            form.save()
            
            if telefono:
                usuario.telefono = telefono
                usuario.save()
                
            messages.success(request, "Datos de cliente guardados.")
            return redirect('home')
    else:
        form = ClienteForm(instance=cliente)

    return render(request, 'registro/completar_cliente.html', {"form": form})


@login_required
def completar_repartidor(request):
    usuario = get_object_or_404(Usuario, user=request.user, tipo_usuario='repartidor')
    repartidor, created = Repartidor.objects.get_or_create(id_repartidor=usuario)

    if request.method == 'POST':
        form = RepartidorForm(request.POST, instance=repartidor)
        telefono = request.POST.get("telefono", "").strip()
        
        if form.is_valid():
            form.save()
            
            if telefono:
                usuario.telefono = telefono
                usuario.save()
            
            messages.success(request, "Datos de repartidor guardados.")
            return redirect('home')
    else:
        form = RepartidorForm(instance=repartidor)

    return render(request, 'registro/completar_repartidor.html', {"form": form})

# VISTA CLIENTE: PARA CONFIRMAR LA ENTREGA
@login_required
def confirmar_entrega(request, pedido_id):
    if request.method != 'POST':
        return redirect('mis_pedidos')

    usuario = get_object_or_404(Usuario, user=request.user, tipo_usuario='cliente')
    cliente = get_object_or_404(Cliente, id_cliente=usuario)

    pedido = get_object_or_404(Pedido, pk=pedido_id, cliente=cliente)

    if pedido.estado != 'asignado':
        return HttpResponseForbidden("Este pedido no puede confirmarse.")

    pedido.estado = 'entregado'
    pedido.save()

    messages.success(request, f"Has confirmado la entrega del pedido #{pedido.id_pedido}.")
    return redirect('mis_pedidos')