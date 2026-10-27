import json
import uuid
from decimal import Decimal
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone

from .models import (
    Usuario,
    Categoria,
    Proveedor,
    Producto,
    Inventario,
    Orden,
    Pago,
    DetalleVenta,
    Direccion
)


def get_user_role(user):
    """Retorna el rol del usuario actual: 'admin', 'cajero', o 'cliente'."""
    if not user.is_authenticated:
        return None
    if user.is_superuser:
        return 'admin'
    perfil = getattr(user, 'perfil', None)
    if perfil:
        return perfil.rol
    if user.groups.filter(name='Cajeros').exists() or user.username.lower().startswith('cajer'):
        return 'cajero'
    return 'cliente'


def index(request):
    """
    Vista principal que presenta el ecosistema completo de Semiconductores y Mecatrónica
    organizado en sus colecciones principales y anexas sobre MongoDB.
    """
    usuarios = Usuario.objects.all().order_by('-creado_en')
    categorias = Categoria.objects.all().order_by('nombre')
    proveedores = Proveedor.objects.all().order_by('nombre')
    productos = Producto.objects.select_related('categoria', 'proveedor').all().order_by('-creado_en')
    inventarios = Inventario.objects.select_related('producto').all()
    ordenes = Orden.objects.select_related('usuario').all().order_by('-creado_en')
    pagos = Pago.objects.select_related('orden').all().order_by('-fecha_transaccion')

    db_name = settings.DATABASES['default']['NAME']
    user_role = get_user_role(request.user)

    # Métricas para el dashboard ejecutivo
    conteos = {
        'users': usuarios.count(),
        'products': productos.count(),
        'categories': categorias.count(),
        'inventory': inventarios.count(),
        'orders': ordenes.count(),
        'payments': pagos.count(),
        'suppliers': proveedores.count(),
    }

    return render(request, 'miapp/index.html', {
        'db_name': db_name,
        'conteos': conteos,
        'usuarios': usuarios[:6],
        'categorias': categorias,
        'proveedores': proveedores,
        'productos': productos[:8],
        'inventarios': inventarios[:8],
        'ordenes': ordenes[:6],
        'pagos': pagos[:6],
        'user_role': user_role,
    })


def login_view(request):
    """
    Pantalla de inicio de sesión con soporte para roles (Administrador y Cajero).
    """
    if request.user.is_authenticated:
        rol = get_user_role(request.user)
        if rol == 'cajero':
            return redirect('modulo_cajero')
        return redirect('index')

    error_msg = None
    if request.method == 'POST':
        usuario_input = request.POST.get('username', '').strip()
        password_input = request.POST.get('password', '').strip()
        user = authenticate(request, username=usuario_input, password=password_input)
        if user is not None:
            login(request, user)
            rol = get_user_role(user)
            if rol == 'cajero':
                return redirect('modulo_cajero')
            return redirect('index')
        else:
            error_msg = "Credenciales incorrectas. Verifica el usuario y la contraseña."

    return render(request, 'miapp/login.html', {
        'error_msg': error_msg,
    })


def logout_view(request):
    """Cierra la sesión del usuario actual."""
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def modulo_cajero(request):
    """
    Módulo de Punto de Venta (POS) y Carrito de Compras exclusivo para el rol de CAJERO
    (o Administrador).
    Control de privilegios: El cajero solo puede vender, cobrar y registrar el detalle,
    sin privilegios para alterar el inventario ni modificar productos.
    """
    rol = get_user_role(request.user)
    if rol not in ['cajero', 'admin']:
        # Acceso denegado si no es cajero
        return render(request, 'miapp/acceso_denegado.html', {
            'motivo': 'Este módulo es exclusivo para usuarios con el rol de Cajero / Operador de Ventas.'
        }, status=403)

    # Obtener catálogo de productos con sus existencias de inventario
    productos = Producto.objects.filter(activo=True).select_related('categoria', 'proveedor')
    
    # Mapear stock disponible por cada producto
    inventarios = {inv.producto_id: inv for inv in Inventario.objects.all()}
    
    productos_data = []
    for p in productos:
        inv = inventarios.get(p.id)
        stock_disp = inv.stock_disponible if inv else 0
        
        # Serializar tiers de precios escalonados para que el carrito dinámico calcule descuentos
        tiers = []
        if p.precios_escalonados:
            for t in p.precios_escalonados:
                tiers.append({
                    'min_qty': t.cantidad_minima,
                    'price': float(t.precio_unitario)
                })
            # Ordenar por cantidad mínima ascendente
            tiers.sort(key=lambda x: x['min_qty'])

        productos_data.append({
            'id': str(p.id),
            'sku': p.sku,
            'nombre': p.nombre,
            'categoria': p.categoria.nombre if p.categoria else 'General',
            'proveedor': p.proveedor.nombre if p.proveedor else 'Genérico',
            'precio_base': float(p.precio_base),
            'encapsulado': p.encapsulado or '',
            'voltaje': p.voltaje_operacion or '',
            'pines': p.pines or '',
            'stock': stock_disp,
            'ubicacion': inv.ubicacion_anaquel if inv else 'Sin asignar',
            'tiers': tiers
        })

    # Clientes disponibles para la venta
    clientes = Usuario.objects.filter(activo=True).order_by('nombre_completo')

    # Últimas 5 órdenes registradas por cajero para visualización rápida
    ultimas_ordenes = Orden.objects.all().order_by('-creado_en')[:5]

    return render(request, 'miapp/cajero_pos.html', {
        'productos_json': json.dumps(productos_data),
        'productos': productos_data,
        'clientes': clientes,
        'ultimas_ordenes': ultimas_ordenes,
        'usuario_cajero': request.user,
        'rol': rol,
    })


@require_POST
@login_required(login_url='login')
def procesar_venta_cajero(request):
    """
    API endpoint para procesar y consolidar la venta del cajero con carrito de compras.
    - Valida rol de cajero (con pocos privilegios; no puede modificar inventario arbitrariamente).
    - Valida y descuenta automáticamente el stock disponible.
    - Registra la Orden con su instantánea de productos (`items` DetalleVenta embebidos).
    - Registra la transacción de Pago.
    - Retorna el detalle para el ticket de venta.
    """
    rol = get_user_role(request.user)
    if rol not in ['cajero', 'admin']:
        return JsonResponse({'success': False, 'error': 'No tienes permisos de Cajero para procesar ventas.'}, status=403)

    try:
        data = json.loads(request.body)
        items_carrito = data.get('items', [])
        cliente_id = data.get('cliente_id')
        metodo_pago = data.get('metodo_pago', 'tarjeta')
        notas = data.get('notas', '')

        if not items_carrito:
            return JsonResponse({'success': False, 'error': 'El carrito de compras está vacío.'}, status=400)

        # 1. Resolver Cliente
        cliente = None
        if cliente_id:
            cliente = Usuario.objects.filter(id=cliente_id).first()
        if not cliente:
            # Asignar al usuario cajero o cliente mostrador predeterminado
            cliente = Usuario.objects.filter(username=request.user.username).first()
            if not cliente:
                cliente = Usuario.objects.first()

        # 2. Validar inventario de cada producto antes de proceder
        productos_map = {}
        for item in items_carrito:
            p_id = item.get('id')
            cantidad = int(item.get('cantidad', 1))
            producto = Producto.objects.filter(id=p_id).first()
            if not producto:
                return JsonResponse({'success': False, 'error': f'Producto ID {p_id} no encontrado.'}, status=404)
            
            inv = Inventario.objects.filter(producto=producto).first()
            if not inv or inv.stock_disponible < cantidad:
                disp = inv.stock_disponible if inv else 0
                return JsonResponse({
                    'success': False,
                    'error': f'Stock insuficiente para {producto.sku}. Disponible: {disp}, Solicitado: {cantidad}'
                }, status=400)
            
            productos_map[p_id] = (producto, inv, cantidad)

        # 3. Construir items de DetalleVenta (Instantánea Inmutable)
        detalles_embebidos = []
        subtotal_acumulado = Decimal('0.00')

        for item in items_carrito:
            p_id = item.get('id')
            producto, inv, cantidad = productos_map[p_id]
            precio_unitario = Decimal(str(item.get('precio_unitario', producto.precio_base)))
            subtotal_item = precio_unitario * cantidad
            subtotal_acumulado += subtotal_item

            detalles_embebidos.append(
                DetalleVenta(
                    producto_id=str(producto.id),
                    sku=producto.sku,
                    nombre=producto.nombre,
                    encapsulado=producto.encapsulado or '',
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    subtotal=subtotal_item
                )
            )

        # 4. Generar Folio Único Correlativo
        timestamp_str = timezone.now().strftime('%Y%m%d%H%M')
        rnd_code = uuid.uuid4().hex[:4].upper()
        folio = f"POS-{timestamp_str}-{rnd_code}"

        costo_envio = Decimal('0.00')  # Venta física en mostrador de caja
        total_venta = subtotal_acumulado + costo_envio

        # 5. Crear la Orden consolidada en MongoDB con detalle embebido
        orden = Orden.objects.create(
            folio=folio,
            usuario=cliente,
            estado='pagada',
            items=detalles_embebidos,
            subtotal=subtotal_acumulado,
            costo_envio=costo_envio,
            total=total_venta,
            direccion_entrega=cliente.direccion_envio if cliente else None,
            notas=f"Venta en Caja registrada por cajero: {request.user.username}. {notas}".strip()
        )

        # 6. Descontar del inventario físico (sin que el cajero tenga permisos para alterar otros campos)
        for p_id, (producto, inv, cantidad) in productos_map.items():
            inv.descontar_venta_directa(cantidad)

        # 7. Registrar transacción en pagos
        transaccion_id = f"PAY-{uuid.uuid4().hex[:12].upper()}"
        pago = Pago.objects.create(
            orden=orden,
            pasarela=metodo_pago,
            transaccion_id=transaccion_id,
            monto=total_venta,
            moneda='MXN',
            estado='aprobado',
            datos_conciliacion={
                'terminal': 'CAJA-POS-01',
                'cajero': request.user.username,
                'metodo': metodo_pago,
                'fecha_hora': timezone.now().isoformat(),
                'tipo_venta': 'mostrador_carrito'
            }
        )

        # 8. Retornar respuesta estructurada para el ticket
        return JsonResponse({
            'success': True,
            'ticket': {
                'folio': orden.folio,
                'fecha': orden.creado_en.strftime('%d/%m/%Y %H:%M:%S'),
                'cajero': request.user.get_full_name() or request.user.username,
                'cliente': cliente.nombre_completo if cliente else 'Cliente de Mostrador',
                'items': [
                    {
                        'sku': d.sku,
                        'nombre': d.nombre,
                        'cantidad': d.cantidad,
                        'precio_unitario': float(d.precio_unitario),
                        'subtotal': float(d.subtotal)
                    }
                    for d in orden.items
                ],
                'subtotal': float(orden.subtotal),
                'costo_envio': float(orden.costo_envio),
                'total': float(orden.total),
                'metodo_pago': pago.get_pasarela_display(),
                'transaccion_id': pago.transaccion_id
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error al procesar la venta: {str(e)}'}, status=500)
