from django.contrib import admin
from .models import (
    Usuario,
    Categoria,
    Proveedor,
    Producto,
    Inventario,
    Orden,
    Pago
)


def es_cajero(user):
    """Verifica si el usuario autenticado tiene el rol de cajero (pocos privilegios)."""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return False
    perfil = getattr(user, 'perfil', None)
    if perfil and perfil.rol == 'cajero':
        return True
    if user.groups.filter(name='Cajeros').exists() or user.username.lower().startswith('cajer'):
        return True
    return False


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'nombre_completo', 'email', 'rol', 'user', 'activo', 'creado_en')
    search_fields = ('username', 'nombre_completo', 'email', 'telefono')
    list_filter = ('rol', 'activo', 'creado_en')
    ordering = ('-creado_en',)

    def has_module_permission(self, request):
        # El cajero no tiene acceso a gestionar cuentas ni roles de usuarios
        if es_cajero(request.user):
            return False
        return super().has_module_permission(request)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'parent', 'activa')
    search_fields = ('nombre', 'slug', 'descripcion')
    list_filter = ('activa', 'parent')
    prepopulated_fields = {'slug': ('nombre',)}

    def has_module_permission(self, request):
        if es_cajero(request.user):
            return False
        return super().has_module_permission(request)


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'pais', 'email_contacto', 'telefono', 'activo', 'creado_en')
    search_fields = ('nombre', 'codigo', 'email_contacto', 'lineas_componentes')
    list_filter = ('activo', 'pais', 'creado_en')
    ordering = ('nombre',)

    def has_module_permission(self, request):
        if es_cajero(request.user):
            return False
        return super().has_module_permission(request)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('sku', 'nombre', 'categoria', 'proveedor', 'precio_base', 'encapsulado', 'voltaje_operacion', 'activo')
    search_fields = ('sku', 'nombre', 'encapsulado', 'descripcion')
    list_filter = ('activo', 'categoria', 'proveedor', 'encapsulado')
    ordering = ('sku',)

    # El cajero puede ver el catálogo pero no alterar productos ni precios
    def has_change_permission(self, request, obj=None):
        if es_cajero(request.user):
            return False
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request):
        if es_cajero(request.user):
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        if es_cajero(request.user):
            return False
        return super().has_delete_permission(request, obj)


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    """
    Control de Inventario y Almacén:
    Por regla estricta de negocio, el rol CAJERO no tiene privilegios de inventario.
    """
    list_display = ('producto', 'stock_disponible', 'stock_reservado', 'ubicacion_anaquel', 'almacen', 'stock_minimo_alerta', 'actualizado_en')
    search_fields = ('producto__sku', 'producto__nombre', 'ubicacion_anaquel', 'almacen')
    list_filter = ('almacen',)
    readonly_fields = ('actualizado_en',)

    def has_module_permission(self, request):
        # Bloqueado totalmente para cajeros: no ven el módulo
        if es_cajero(request.user):
            return False
        return super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        if es_cajero(request.user):
            return False
        return super().has_view_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if es_cajero(request.user):
            return False
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request):
        if es_cajero(request.user):
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        if es_cajero(request.user):
            return False
        return super().has_delete_permission(request, obj)


@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ('folio', 'usuario', 'estado', 'subtotal', 'costo_envio', 'total', 'creado_en')
    search_fields = ('folio', 'usuario__username', 'usuario__email', 'usuario__nombre_completo')
    list_filter = ('estado', 'creado_en')
    readonly_fields = ('creado_en', 'actualizado_en')
    ordering = ('-creado_en',)

    # El cajero sí puede ver y registrar órdenes de venta
    def has_delete_permission(self, request, obj=None):
        if es_cajero(request.user):
            return False
        return super().has_delete_permission(request, obj)


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('transaccion_id', 'orden', 'pasarela', 'monto', 'moneda', 'estado', 'fecha_transaccion')
    search_fields = ('transaccion_id', 'orden__folio')
    list_filter = ('pasarela', 'estado', 'moneda', 'fecha_transaccion')
    readonly_fields = ('fecha_transaccion',)
    ordering = ('-fecha_transaccion',)

    def has_delete_permission(self, request, obj=None):
        if es_cajero(request.user):
            return False
        return super().has_delete_permission(request, obj)
