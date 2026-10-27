# Proyecto Django con MongoDB

Proyecto configurado con la última versión de **Django (6.1)** y el backend oficial de MongoDB: **`django-mongodb-backend`**, con soporte completo para **Django Admin**, autenticación y migraciones.

---

## 🚀 Cómo Iniciar el Servidor

1. **Activar el entorno virtual:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   *(o en bash/cmd: `source .venv/Scripts/activate` o `.\.venv\Scripts\activate.bat`)*

2. **Verificar que MongoDB esté corriendo:**
   Por defecto está configurado para conectarse a `mongodb://localhost:27017/` en la base de datos `djangopractica_db`.

3. **Ejecutar el servidor de desarrollo:**
   ```powershell
   python manage.py runserver
   ```

4. **Acceder en el navegador:**
   - **Página de inicio:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
   - **Panel de Administración (Django Admin):** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🔑 Credenciales y Roles de Acceso

El sistema cuenta con control de acceso basado en roles (**RBAC**):

### 1. 👑 Administrador (Acceso Total)
- **Usuario:** `admin`
- **Contraseña:** `admin1234`
- **Privilegios:** Acceso completo a Django Admin, configuración, catálogo y gestión de inventario.

### 2. 💼 Cajero / Operador de Ventas (Punto de Venta POS)
- **Usuario:** `cajero`
- **Contraseña:** `cajero1234`
- **Módulo POS / Carrito:** [http://127.0.0.1:8000/caja/](http://127.0.0.1:8000/caja/)
- **Privilegios:**
  - ✅ Operación del carrito de ventas en mostrador (POS).
  - ✅ Cálculo dinámico de subtotales y descuentos por volumen (tiers).
  - ✅ Procesamiento de ventas, cobro y generación de ticket con detalle embebido.
  - ❌ **Sin privilegios de inventario:** Bloqueado el acceso a modificar existencias o alterar la base de datos.

### 3. 🔬 Ingeniero / Maker Mecatrónico
- **Usuario:** `cmendoza`
- **Contraseña:** `ingeniero1234`
- **Perfil:** Carlos Mendoza (`carlos.mendoza@robotech.mx`)
- **Privilegios:** Consulta técnica de especificaciones, encapsulados, datasheets y proyectos.

### 4. 🏢 Distribuidor Mayorista
- **Usuario:** `electromayoreo`
- **Contraseña:** `distribuidor1234`
- **Perfil:** ElectroMayoreo Industrial (`ventas@electromayoreo.com`)
- **Privilegios:** Acceso al catálogo con aplicación de precios escalonados (tiers) por volumen de compra.

### 5. 👤 Cliente Retail
- **Usuario:** `cliente`
- **Contraseña:** `cliente1234`
- **Perfil:** Ana López (`cliente@ejemplo.com`)
- **Privilegios:** Navegación en catálogo general, compras al menudeo y visualización de pedidos.

---

## ⚙️ Configuración en `config/settings.py`

### 1. Conexión a MongoDB (`DATABASES`)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django_mongodb_backend',
        'HOST': 'mongodb://localhost:27017/', # o tu cadena de MongoDB Atlas
        'NAME': 'djangopractica_db',
    },
}

DATABASE_ROUTERS = ["django_mongodb_backend.routers.MongoRouter"]
```

### 2. Clave primaria por defecto (`DEFAULT_AUTO_FIELD`)
MongoDB utiliza `ObjectId` en lugar de IDs enteros incrementales de SQL:
```python
DEFAULT_AUTO_FIELD = 'django_mongodb_backend.fields.ObjectIdAutoField'
```

### 3. Configuración de `INSTALLED_APPS` para el Admin de Django
Para que el Admin y la autenticación funcionen con los `ObjectId` de MongoDB, se utilizan subclases de `AppConfig` definidas en `config/apps.py`:
```python
INSTALLED_APPS = [
    'config.apps.MongoAdminConfig',
    'config.apps.MongoAuthConfig',
    'config.apps.MongoContentTypesConfig',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_mongodb_backend',
    'miapp.apps.MiappConfig',
]
```

### 4. Módulos de migración (`MIGRATION_MODULES`)
Permiten a Django aplicar las migraciones compatibles con MongoDB para las tablas del sistema:
```python
MIGRATION_MODULES = {
    'admin': 'mongo_migrations.admin',
    'auth': 'mongo_migrations.auth',
    'contenttypes': 'mongo_migrations.contenttypes',
}
```

---

## 📦 Estructura del Proyecto

- **`config/`**: Configuración principal de Django (`settings.py`, `urls.py`, `apps.py`).
- **`miapp/`**: Aplicación con los modelos y colecciones de Semiconductores y Mecatrónica.
- **`mongo_migrations/`**: Migraciones pre-configuradas para compatibilidad con MongoDB.
- **`requirements.txt`**: Dependencias instaladas.
- **`.venv/`**: Entorno virtual con todas las librerías instaladas.

---

## 🗄️ Colecciones Principales y Anexas Implementadas (MongoDB)

1. **`users` (Clientes y Cuentas)**:
   - Colección: `users` (Modelo: `Usuario`)
   - Autenticación, perfiles, roles (`cliente`, `distribuidor`, `ingeniero`, `admin`) y direcciones embebidas (`Direccion`) para envío y facturación.
2. **`products` (Semiconductores y Mecatrónica)**:
   - Colección: `products` (Modelo: `Producto`)
   - Especificaciones técnicas flexibles (datasheet, encapsulado, pines, voltajes, JSON), relación jerárquica con categorías y precios escalonados por volumen (`PrecioEscalonado`).
3. **`categories` (Categorización Jerárquica)**:
   - Colección: `categories` (Modelo: `Categoria`)
   - Clasificación en árbol recursiva para componentes (ej: *Microcontroladores > ARM Cortex > STM32*).
4. **`inventory` (Gestión de Stock en Almacén)**:
   - Colección: `inventory` (Modelo: `Inventario`)
   - Desacoplado del catálogo de productos para evitar contención de escrituras. Control de stock disponible, reservaciones para checkout, ubicación física de anaqueles/gavetas y alertas de reorden.
5. **`orders` (Transacción Comercial Consolidada)**:
   - Colección: `orders` (Modelo: `Orden`)
   - Venta con detalle embebido (`DetalleVenta` como instantánea / snapshot inmutable de precios y cantidades al momento de la compra), estados y dirección de entrega embebida.
6. **`payments` (Anexa - Pasarelas y Conciliación)**:
   - Colección: `payments` (Modelo: `Pago`)
   - Transacciones con Stripe, PayPal, transferencias bancarias, tokens de cobro y conciliación JSON.
7. **`suppliers` (Anexa - Fabricantes y Distribuidores)**:
   - Colección: `suppliers` (Modelo: `Proveedor`)
   - Fabricantes de semiconductores (Texas Instruments, STMicroelectronics, Microchip) y líneas de distribución.

