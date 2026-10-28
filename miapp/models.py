from django.db import models
from django_mongodb_backend.models import EmbeddedModel
from django_mongodb_backend.fields import EmbeddedModelField, EmbeddedModelArrayField


# ==============================================================================
# MODELOS EMBEBIDOS (Subdocumentos de MongoDB)
# ==============================================================================

class Direccion(EmbeddedModel):
    """
    Subdocumento embebido para direcciones de envío y facturación.
    Se almacena directamente dentro del documento de Usuario u Orden.
    """
    calle = models.CharField(max_length=255, verbose_name="Calle y Número")
    colonia = models.CharField(max_length=150, blank=True, verbose_name="Colonia / Asentamiento")
    ciudad = models.CharField(max_length=100, verbose_name="Ciudad / Municipio")
    estado = models.CharField(max_length=100, verbose_name="Estado / Provincia")
    codigo_postal = models.CharField(max_length=20, verbose_name="Código Postal")
    pais = models.CharField(max_length=100, default="México", verbose_name="País")
    referencias = models.CharField(max_length=255, blank=True, verbose_name="Referencias de Entrega")

    class Meta:
        app_label = 'miapp'
        verbose_name = "Dirección"
        verbose_name_plural = "Direcciones"

    def __str__(self):
        return f"{self.calle}, {self.ciudad}, {self.estado} (CP: {self.codigo_postal})"


class PrecioEscalonado(EmbeddedModel):
    """
    Subdocumento embebido para precios escalonados por volumen de compra.
    Permite definir rangos de precio por cantidad (Tiers de Semiconductores).
    """
    cantidad_minima = models.PositiveIntegerField(verbose_name="Cantidad Mínima (Desde)")
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Precio Unitario ($)")

    class Meta:
        app_label = 'miapp'
        verbose_name = "Precio Escalonado por Volumen"
        verbose_name_plural = "Precios Escalonados"

    def __str__(self):
        return f"≥ {self.cantidad_minima} uds: ${self.precio_unitario}"


class DetalleVenta(EmbeddedModel):
    """
    Subdocumento embebido que representa la instantánea (snapshot) fija
    del producto vendido en el momento exacto de la compra.
    """
    producto_id = models.CharField(max_length=100, verbose_name="ID Producto")
    sku = models.CharField(max_length=100, verbose_name="SKU / No. Parte")
    nombre = models.CharField(max_length=250, verbose_name="Nombre del Componente")
    encapsulado = models.CharField(max_length=100, blank=True, verbose_name="Encapsulado")
    cantidad = models.PositiveIntegerField(default=1, verbose_name="Cantidad Comprada")
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Precio Unitario (Instantánea)")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Subtotal ($)")

    class Meta:
        app_label = 'miapp'
        verbose_name = "Detalle de Venta Embebido"
        verbose_name_plural = "Detalles de Venta"

    def __str__(self):
        return f"{self.cantidad}x {self.sku} (${self.precio_unitario} c/u = ${self.subtotal})"


# ==============================================================================
# COLECCIONES PRINCIPALES Y ANEXAS DEL SISTEMA
# ==============================================================================

class Usuario(models.Model):
    """
    Colección: 'users'
    Clientes y Cuentas: Información de autenticación, perfiles,
    direcciones de envío/facturación (embebidas) y roles.
    """
    ROLES = [
        ('admin', 'Administrador'),
        ('cajero', 'Cajero / Operador de Ventas'),
        ('cliente', 'Cliente'),
        ('distribuidor', 'Distribuidor Mayorista'),
        ('ingeniero', 'Ingeniero / Maker Mecatrónico'),
    ]

    user = models.OneToOneField(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='perfil',
        verbose_name="Cuenta de Autenticación Django"
    )
    username = models.CharField(max_length=100, unique=True, verbose_name="Nombre de Usuario")
    email = models.EmailField(unique=True, verbose_name="Correo Electrónico")
    nombre_completo = models.CharField(max_length=200, verbose_name="Nombre Completo")
    telefono = models.CharField(max_length=30, blank=True, verbose_name="Teléfono de Contacto")
    rol = models.CharField(max_length=30, choices=ROLES, default='cliente', verbose_name="Rol")
    
    # Direcciones embebidas como subdocumentos de MongoDB
    direccion_envio = EmbeddedModelField(Direccion, null=True, blank=True, verbose_name="Dirección de Envío (Embebida)")
    direccion_facturacion = EmbeddedModelField(Direccion, null=True, blank=True, verbose_name="Dirección de Facturación (Embebida)")
    
    activo = models.BooleanField(default=True, verbose_name="Cuenta Activa")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        db_table = 'users'
        verbose_name = "Usuario (Cliente / Cuenta)"
        verbose_name_plural = "users (Clientes y Cuentas)"

    @property
    def es_admin(self):
        return self.rol == 'admin' or (self.user and self.user.is_superuser)

    @property
    def es_cajero(self):
        return self.rol == 'cajero'

    def __str__(self):
        return f"{self.nombre_completo} (@{self.username}) [{self.get_rol_display()}]"


class Categoria(models.Model):
    """
    Colección: 'categories'
    Categorización jerárquica para componentes
    (e.g., Microcontroladores > ARM Cortex > STM32).
    """
    nombre = models.CharField(max_length=150, verbose_name="Nombre de Categoría")
    slug = models.SlugField(max_length=150, unique=True, verbose_name="Slug")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategorias',
        verbose_name="Categoría Padre (Jerarquía)"
    )
    activa = models.BooleanField(default=True, verbose_name="Activa")

    class Meta:
        db_table = 'categories'
        verbose_name = "Categoría de Componentes"
        verbose_name_plural = "categories (Categorización Jerárquica)"

    def ruta_jerarquica(self):
        """Retorna la ruta completa jerárquica: Padre > Hijo > Subhijo"""
        if self.parent:
            return f"{self.parent.ruta_jerarquica()} > {self.nombre}"
        return self.nombre

    def __str__(self):
        return self.ruta_jerarquica()


class Proveedor(models.Model):
    """
    Colección: 'suppliers' (Anexa)
    Información de fabricantes y distribuidores de componentes electrónicos
    (e.g., Texas Instruments, STMicroelectronics).
    """
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Fabricante / Proveedor")
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código / Siglas (ej: TI, ST, NXP)")
    sitio_web = models.URLField(blank=True, verbose_name="Sitio Web Oficial")
    email_contacto = models.EmailField(blank=True, verbose_name="Email de Contacto")
    telefono = models.CharField(max_length=50, blank=True, verbose_name="Teléfono")
    pais = models.CharField(max_length=100, default="Estados Unidos", verbose_name="País de Origen")
    lineas_componentes = models.TextField(blank=True, verbose_name="Líneas de Especialidad / Semiconductores")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        db_table = 'suppliers'
        verbose_name = "Proveedor / Fabricante"
        verbose_name_plural = "suppliers (Proveedores y Fabricantes)"

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"


class Producto(models.Model):
    """
    Colección: 'products'
    Semiconductores y Mecatrónica: Catálogo con especificaciones técnicas
    flexibles (datasheet, encapsulado, voltaje, pines), precios escalonados
    por volumen y categoría.
    """
    sku = models.CharField(max_length=100, unique=True, verbose_name="SKU / No. de Parte Fabricante (MPN)")
    nombre = models.CharField(max_length=250, verbose_name="Nombre / Título del Componente")
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos', verbose_name="Categoría")
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos', verbose_name="Fabricante / Proveedor")
    precio_base = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Precio Base Unitario (1 ud)")
    descripcion = models.TextField(blank=True, verbose_name="Descripción Técnica")

    imagen_url = models.CharField(max_length=255, blank=True, default='', verbose_name="URL de Imagen del Producto")

    # Especificaciones técnicas flexibles
    datasheet_url = models.URLField(blank=True, verbose_name="URL del Datasheet Oficial")
    encapsulado = models.CharField(max_length=100, blank=True, verbose_name="Encapsulado / Package (ej. LQFP-64, SOIC-8, TO-220)")
    voltaje_operacion = models.CharField(max_length=100, blank=True, verbose_name="Voltaje de Operación (ej. 1.8V - 3.6V, 5V)")
    pines = models.PositiveIntegerField(null=True, blank=True, verbose_name="Número de Pines / Leads")
    especificaciones_tecnicas = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Especificaciones Flexibles (JSON: frecuencia, memoria flash, torque, etc.)"
    )

    # Precios escalonados por volumen (Array embebido de subdocumentos)
    precios_escalonados = EmbeddedModelArrayField(
        PrecioEscalonado,
        blank=True,
        default=list,
        verbose_name="Precios Escalonados por Volumen"
    )

    activo = models.BooleanField(default=True, verbose_name="Activo en Catálogo")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        db_table = 'products'
        verbose_name = "Producto (Semiconductores y Mecatrónica)"
        verbose_name_plural = "products (Semiconductores y Mecatrónica)"

    @property
    def get_imagen_url(self):
        """Retorna la URL de la imagen del producto, con fallback automático inteligente según SKU."""
        if self.imagen_url:
            return self.imagen_url
        sku_map = {
            'STM32F401RET6': '/static/miapp/img/products/stm32f401.jpg',
            'ESP32-WROOM-32D': '/static/miapp/img/products/esp32.jpg',
            'ATMEGA328P-PU': '/static/miapp/img/products/atmega328p.jpg',
            'DRV8825': '/static/miapp/img/products/drv8825.jpg',
            'L298N-MOD': '/static/miapp/img/products/l298n.jpg',
            'MPU-6050': '/static/miapp/img/products/mpu6050.jpg',
            'INA219': '/static/miapp/img/products/ina219.jpg',
            'NEMA17-17HS4401': '/static/miapp/img/products/nema17.jpg',
        }
        return sku_map.get(self.sku, '/static/miapp/img/products/stm32f401.jpg')

    def __str__(self):
        return f"{self.sku} - {self.nombre}"


class Inventario(models.Model):
    """
    Colección: 'inventory'
    Gestión de stock en almacén, reservaciones para órdenes en checkout y
    ubicación física de anaqueles. Separar inventario del catálogo evita
    bloqueos frecuentes de escritura en la colección de productos cuando
    cambian las cantidades.
    """
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE, related_name='inventario', verbose_name="Producto Asociado")
    stock_disponible = models.PositiveIntegerField(default=0, verbose_name="Stock Disponible")
    stock_reservado = models.PositiveIntegerField(default=0, verbose_name="Stock Reservado (En Checkout)")
    ubicacion_anaquel = models.CharField(max_length=100, blank=True, verbose_name="Ubicación Física (Anaquel / Pasillo / Gaveta)")
    almacen = models.CharField(max_length=100, default="Almacén Central Mecatrónica", verbose_name="Almacén")
    stock_minimo_alerta = models.PositiveIntegerField(default=10, verbose_name="Stock Mínimo para Alerta de Reorden")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Última Actualización de Stock")

    class Meta:
        db_table = 'inventory'
        verbose_name = "Inventario de Almacén"
        verbose_name_plural = "inventory (Gestión de Stock y Anaqueles)"

    @property
    def stock_total(self):
        return self.stock_disponible + self.stock_reservado

    def reservar(self, cantidad):
        """Bloquea stock para órdenes en proceso de checkout."""
        if self.stock_disponible >= cantidad:
            self.stock_disponible -= cantidad
            self.stock_reservado += cantidad
            self.save(update_fields=['stock_disponible', 'stock_reservado', 'actualizado_en'])
            return True
        return False

    def liberar_reserva(self, cantidad):
        """Libera stock si el checkout expira o se cancela."""
        cant = min(self.stock_reservado, cantidad)
        self.stock_reservado -= cant
        self.stock_disponible += cant
        self.save(update_fields=['stock_disponible', 'stock_reservado', 'actualizado_en'])

    def confirmar_venta(self, cantidad):
        """Descuenta permanentemente de stock reservado al pagar la orden."""
        cant = min(self.stock_reservado, cantidad)
        self.stock_reservado -= cant
        self.save(update_fields=['stock_reservado', 'actualizado_en'])

    def descontar_venta_directa(self, cantidad):
        """Descuenta directamente del stock disponible al cobrar una venta en punto de venta / caja."""
        if self.stock_disponible >= cantidad:
            self.stock_disponible -= cantidad
            self.save(update_fields=['stock_disponible', 'actualizado_en'])
            return True
        return False

    def __str__(self):
        return f"Stock de {self.producto.sku}: {self.stock_disponible} disp. / {self.stock_reservado} res. [{self.ubicacion_anaquel}]"


class Orden(models.Model):
    """
    Colección: 'orders'
    Venta + Detalle de Venta embebido: La transacción comercial consolidada.
    Incluye la instantánea de los productos vendidos con sus precios fijos
    en el momento de la compra.
    """
    ESTADOS = [
        ('pendiente', 'Pendiente de Pago'),
        ('pagada', 'Pagada / Confirmada'),
        ('preparando', 'Preparando en Almacén'),
        ('enviada', 'Enviada'),
        ('entregada', 'Entregada'),
        ('cancelada', 'Cancelada'),
    ]

    folio = models.CharField(max_length=50, unique=True, verbose_name="Folio de Orden")
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='ordenes', verbose_name="Cliente")
    estado = models.CharField(max_length=30, choices=ESTADOS, default='pendiente', verbose_name="Estado de la Orden")
    
    # Detalle de venta embebido (Instantánea de productos y precios al momento de comprar)
    items = EmbeddedModelArrayField(DetalleVenta, verbose_name="Detalle de Venta (Instantánea Embebida)")

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, verbose_name="Subtotal ($)")
    costo_envio = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, verbose_name="Costo de Envío ($)")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, verbose_name="Total Consolidado ($)")

    direccion_entrega = EmbeddedModelField(Direccion, null=True, blank=True, verbose_name="Dirección de Entrega (Instantánea)")
    notas = models.TextField(blank=True, verbose_name="Notas de Compra / Instrucciones")

    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        db_table = 'orders'
        verbose_name = "Orden de Venta"
        verbose_name_plural = "orders (Venta + Detalle de Venta Embebido)"

    def __str__(self):
        return f"Orden {self.folio} - {self.usuario.username} (${self.total}) [{self.get_estado_display()}]"


class Pago(models.Model):
    """
    Colección: 'payments' (Anexa)
    Registro de transacciones con pasarelas de pago (Stripe, PayPal, transferencias),
    tokens de cobro y conciliación.
    """
    PASARELAS = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('transferencia', 'Transferencia Bancaria SPEI'),
        ('tarjeta', 'Tarjeta Bancaria / Terminal'),
    ]

    ESTADOS_PAGO = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado / Conciliado'),
        ('rechazado', 'Rechazado / Fallido'),
        ('reembolsado', 'Reembolsado'),
    ]

    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='pagos', verbose_name="Orden de Compra")
    pasarela = models.CharField(max_length=50, choices=PASARELAS, verbose_name="Pasarela de Pago")
    transaccion_id = models.CharField(max_length=200, unique=True, verbose_name="ID de Transacción / Token de Cobro")
    monto = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Monto Transaccionado ($)")
    moneda = models.CharField(max_length=10, default="MXN", verbose_name="Moneda")
    estado = models.CharField(max_length=30, choices=ESTADOS_PAGO, default='pendiente', verbose_name="Estado de Pago")
    
    # Conciliación y tokens de la pasarela
    datos_conciliacion = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos de Conciliación y Respuesta de Pasarela (JSON)"
    )
    fecha_transaccion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Transacción")

    class Meta:
        db_table = 'payments'
        verbose_name = "Transacción de Pago"
        verbose_name_plural = "payments (Registro de Pasarelas y Conciliación)"

    def __str__(self):
        return f"Pago {self.transaccion_id} ({self.get_pasarela_display()}) - ${self.monto} {self.moneda} [{self.get_estado_display()}]"
