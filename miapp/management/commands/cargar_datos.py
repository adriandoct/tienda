import uuid
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from miapp.models import (
    Usuario,
    Categoria,
    Proveedor,
    Producto,
    Inventario,
    Orden,
    Pago,
    Direccion,
    PrecioEscalonado,
    DetalleVenta,
)


class Command(BaseCommand):
    help = "Carga la información inicial y datos de prueba para la base de datos MongoDB (Semiconductores y Mecatrónica)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Elimina datos existentes antes de cargar los nuevos registros.',
        )

    def handle(self, *args, **options):
        if options['limpiar']:
            self.stdout.write(self.style.WARNING("Eliminando registros previos en colecciones MongoDB..."))
            Pago.objects.all().delete()
            Orden.objects.all().delete()
            Inventario.objects.all().delete()
            Producto.objects.all().delete()
            Proveedor.objects.all().delete()
            Categoria.objects.all().delete()
            Usuario.objects.all().delete()
            User.objects.filter(username__in=['admin', 'cajero', 'cmendoza', 'electromayoreo', 'cliente']).delete()
            self.stdout.write(self.style.SUCCESS("Colecciones limpiadas exitosamente."))

        self.stdout.write(self.style.HTTP_INFO("=================================================================="))
        self.stdout.write(self.style.HTTP_INFO("  INICIANDO CARGA DE DATOS EN MONGODB (django-mongodb-backend)"))
        self.stdout.write(self.style.HTTP_INFO("=================================================================="))

        # ----------------------------------------------------------------------
        # 1. CATEGORÍAS JERÁRQUICAS (categories)
        # ----------------------------------------------------------------------
        self.stdout.write("\n[1/6] Creando arbol jerarquico de categorias...")

        cat_semiconductores, _ = Categoria.objects.get_or_create(
            slug="semiconductores",
            defaults={
                "nombre": "Semiconductores",
                "descripcion": "Dispositivos semiconductores, circuitos integrados y microcontroladores.",
                "activa": True,
            }
        )

        cat_mcu, _ = Categoria.objects.get_or_create(
            slug="microcontroladores",
            defaults={
                "nombre": "Microcontroladores y Procesadores",
                "descripcion": "MCUs y procesadores embebidos de 8, 16 y 32 bits.",
                "parent": cat_semiconductores,
                "activa": True,
            }
        )

        cat_stm32, _ = Categoria.objects.get_or_create(
            slug="stm32-cortex-m4",
            defaults={
                "nombre": "STM32 Cortex-M4",
                "descripcion": "Microcontroladores STMicroelectronics ARM Cortex-M4 de alto desempeño con DSP y FPU.",
                "parent": cat_mcu,
                "activa": True,
            }
        )

        cat_esp, _ = Categoria.objects.get_or_create(
            slug="espressif-esp32",
            defaults={
                "nombre": "Espressif Wi-Fi & Bluetooth",
                "descripcion": "SoCs inalámbricos ESP32 de doble núcleo para IoT y mecatrónica conectada.",
                "parent": cat_mcu,
                "activa": True,
            }
        )

        cat_avr, _ = Categoria.objects.get_or_create(
            slug="microchip-avr",
            defaults={
                "nombre": "Microchip AVR 8-Bit",
                "descripcion": "Microcontroladores AVR clásicos de alto rendimiento y bajo consumo (ATmega).",
                "parent": cat_mcu,
                "activa": True,
            }
        )

        cat_analog, _ = Categoria.objects.get_or_create(
            slug="analog-drivers",
            defaults={
                "nombre": "Drivers de Motor y Potencia",
                "descripcion": "Controladores de motores a pasos, puentes H y etapas de potencia.",
                "parent": cat_semiconductores,
                "activa": True,
            }
        )

        cat_mecatronica, _ = Categoria.objects.get_or_create(
            slug="sensores-mecatronica",
            defaults={
                "nombre": "Sensores y Mecatrónica",
                "descripcion": "Sensores inerciales, instrumentación, actuadores y robótica.",
                "activa": True,
            }
        )

        cat_sensores_inerciales, _ = Categoria.objects.get_or_create(
            slug="sensores-inerciales-imu",
            defaults={
                "nombre": "Sensores Inerciales y Cinemáticos",
                "descripcion": "Giroscopios, acelerómetros y unidades IMU de 6 y 9 grados de libertad.",
                "parent": cat_mecatronica,
                "activa": True,
            }
        )

        cat_sensores_potencia, _ = Categoria.objects.get_or_create(
            slug="sensores-corriente-potencia",
            defaults={
                "nombre": "Sensores de Corriente y Potencia",
                "descripcion": "Monitores de corriente, voltaje y potencia bidireccionales en bus I2C/SPI.",
                "parent": cat_mecatronica,
                "activa": True,
            }
        )

        cat_actuadores, _ = Categoria.objects.get_or_create(
            slug="actuadores-motores",
            defaults={
                "nombre": "Actuadores y Motores de Precisión",
                "descripcion": "Motores a pasos bipolares NEMA, servomotores y motores DC con reductora.",
                "parent": cat_mecatronica,
                "activa": True,
            }
        )
        self.stdout.write(self.style.SUCCESS(f"  [OK] {Categoria.objects.count()} Categorias listas."))

        # ----------------------------------------------------------------------
        # 2. PROVEEDORES / FABRICANTES (suppliers)
        # ----------------------------------------------------------------------
        self.stdout.write("\n[2/6] Registrando fabricantes y distribuidores de semiconductores...")

        proveedores_data = [
            {
                "codigo": "ST",
                "nombre": "STMicroelectronics",
                "sitio_web": "https://www.st.com",
                "email_contacto": "ventas.latam@st.com",
                "telefono": "+41 22 929 29 29",
                "pais": "Suiza / Francia",
                "lineas_componentes": "Microcontroladores STM32 de 32-bits, Sensores MEMS, Transistores MOSFET y drivers de potencia.",
            },
            {
                "codigo": "TI",
                "nombre": "Texas Instruments",
                "sitio_web": "https://www.ti.com",
                "email_contacto": "support@ti.com",
                "telefono": "+1 800 336 5236",
                "pais": "Estados Unidos",
                "lineas_componentes": "Drivers de motor paso a paso (DRV), Monitores de corriente (INA), Amplificadores operacionales.",
            },
            {
                "codigo": "ESPR",
                "nombre": "Espressif Systems",
                "sitio_web": "https://www.espressif.com",
                "email_contacto": "sales@espressif.com",
                "telefono": "+86 21 6106 2057",
                "pais": "China",
                "lineas_componentes": "SoCs inalámbricos Wi-Fi y Bluetooth, módulos ESP32, ESP32-S3, ESP32-C3 y kits de desarrollo.",
            },
            {
                "codigo": "MCHP",
                "nombre": "Microchip Technology",
                "sitio_web": "https://www.microchip.com",
                "email_contacto": "sales.americas@microchip.com",
                "telefono": "+1 480 792 7200",
                "pais": "Estados Unidos",
                "lineas_componentes": "Microcontroladores de arquitectura AVR y PIC, memorias EEPROM serie y periféricos analógicos.",
            },
            {
                "codigo": "INVN",
                "nombre": "TDK InvenSense",
                "sitio_web": "https://invensense.tdk.com",
                "email_contacto": "contact@invensense.com",
                "telefono": "+1 408 988 7339",
                "pais": "Japón",
                "lineas_componentes": "Sensores inerciales MEMS de alta precisión, giroscopios, acelerómetros de 6 y 9 ejes (MPU series).",
            },
            {
                "codigo": "STP",
                "nombre": "StepperOnline Industrial",
                "sitio_web": "https://www.omc-stepperonline.com",
                "email_contacto": "service@stepperonline.com",
                "telefono": "+1 312 858 8899",
                "pais": "Estados Unidos / China",
                "lineas_componentes": "Motores a pasos NEMA 14/17/23/34, husillos de precisión y controladores industriales CNC.",
            },
        ]

        proveedores_dict = {}
        for pdata in proveedores_data:
            prov, _ = Proveedor.objects.update_or_create(
                codigo=pdata["codigo"],
                defaults=pdata
            )
            proveedores_dict[prov.codigo] = prov

        self.stdout.write(self.style.SUCCESS(f"  [OK] {Proveedor.objects.count()} Proveedores registrados."))

        # ----------------------------------------------------------------------
        # 3. USUARIOS Y ROLES RBAC (users) CON SUBDOCUMENTOS EMBEBIDOS (Direccion)
        # ----------------------------------------------------------------------
        self.stdout.write("\n[3/6] Creando usuarios con roles de acceso y direcciones embebidas...")

        usuarios_datos = [
            {
                "username": "admin",
                "email": "admin@tienda.com",
                "password": "admin1234",
                "nombre_completo": "Administrador General del Sistema",
                "rol": "admin",
                "is_staff": True,
                "is_superuser": True,
                "telefono": "+52 55 9876 5432",
                "dir_envio": Direccion(
                    calle="Circuito Corporativo 100, Edificio A",
                    colonia="Santa Fe",
                    ciudad="Cuajimalpa",
                    estado="Ciudad de México",
                    codigo_postal="05348",
                    pais="México",
                    referencias="Recepción Corporativa Piso 5"
                ),
            },
            {
                "username": "cajero",
                "email": "cajero@tienda.com",
                "password": "cajero1234",
                "nombre_completo": "Operador Punto de Venta (POS)",
                "rol": "cajero",
                "is_staff": False,
                "is_superuser": False,
                "telefono": "+52 55 5555 1212",
                "dir_envio": Direccion(
                    calle="Av. Balderas 44, Mostrador Principal",
                    colonia="Centro",
                    ciudad="Cuauhtémoc",
                    estado="Ciudad de México",
                    codigo_postal="06070",
                    pais="México",
                    referencias="Sucursal Centro - Caja 1"
                ),
            },
            {
                "username": "cmendoza",
                "email": "carlos.mendoza@robotech.mx",
                "password": "ingeniero1234",
                "nombre_completo": "Ing. Carlos Mendoza (RoboTech Lab)",
                "rol": "ingeniero",
                "is_staff": False,
                "is_superuser": False,
                "telefono": "+52 55 1234 5678",
                "dir_envio": Direccion(
                    calle="Av. Insurgentes Sur 1602, Int. 402",
                    colonia="Crédito Constructor",
                    ciudad="Benito Juárez",
                    estado="Ciudad de México",
                    codigo_postal="03940",
                    pais="México",
                    referencias="Torre Insurgentes Corporativo"
                ),
            },
            {
                "username": "electromayoreo",
                "email": "ventas@electromayoreo.com",
                "password": "distribuidor1234",
                "nombre_completo": "ElectroMayoreo Industrial S.A. de C.V.",
                "rol": "distribuidor",
                "is_staff": False,
                "is_superuser": False,
                "telefono": "+52 81 8345 6789",
                "dir_envio": Direccion(
                    calle="Parque Industrial Regiomontano, Nave 14-B",
                    colonia="Zona Industrial",
                    ciudad="Monterrey",
                    estado="Nuevo León",
                    codigo_postal="64000",
                    pais="México",
                    referencias="Andén de Carga y Descarga #4"
                ),
            },
            {
                "username": "cliente",
                "email": "cliente@ejemplo.com",
                "password": "cliente1234",
                "nombre_completo": "Ana López Martínez",
                "rol": "cliente",
                "is_staff": False,
                "is_superuser": False,
                "telefono": "+52 33 9876 5432",
                "dir_envio": Direccion(
                    calle="Calle Prisciliano Sánchez 450",
                    colonia="Americana",
                    ciudad="Guadalajara",
                    estado="Jalisco",
                    codigo_postal="44160",
                    pais="México",
                    referencias="Casa particular con zaguán negro"
                ),
            },
        ]

        usuarios_dict = {}
        for udata in usuarios_datos:
            user_auth, created = User.objects.get_or_create(
                username=udata["username"],
                defaults={
                    "email": udata["email"],
                    "is_staff": udata["is_staff"],
                    "is_superuser": udata["is_superuser"],
                }
            )
            user_auth.set_password(udata["password"])
            user_auth.is_staff = udata["is_staff"]
            user_auth.is_superuser = udata["is_superuser"]
            user_auth.save()

            usuario_perfil, _ = Usuario.objects.update_or_create(
                username=udata["username"],
                defaults={
                    "user": user_auth,
                    "email": udata["email"],
                    "nombre_completo": udata["nombre_completo"],
                    "rol": udata["rol"],
                    "telefono": udata.get("telefono", ""),
                    "direccion_envio": udata.get("dir_envio"),
                    "direccion_facturacion": udata.get("dir_envio"),
                    "activo": True,
                }
            )
            usuarios_dict[usuario_perfil.username] = usuario_perfil

        self.stdout.write(self.style.SUCCESS(f"  [OK] {Usuario.objects.count()} Usuarios y perfiles creados con contraseñas seguras."))

        # ----------------------------------------------------------------------
        # 4. PRODUCTOS (products) CON SUBDOCUMENTOS EMBEBIDOS (PrecioEscalonado)
        # ----------------------------------------------------------------------
        self.stdout.write("\n[4/6] Registrando productos, especificaciones JSON y arrays embebidos de precios escalonados...")

        productos_catalogo = [
            {
                "sku": "STM32F401RET6",
                "nombre": "MCU ARM Cortex-M4 84MHz 512KB Flash",
                "categoria": cat_stm32,
                "proveedor": proveedores_dict["ST"],
                "precio_base": Decimal("125.50"),
                "descripcion": "Microcontrolador de 32 bits de alto rendimiento basado en el núcleo ARM Cortex-M4 con FPU, 84 MHz de reloj, 512 KB de memoria Flash y 96 KB de SRAM.",
                "imagen_url": "/static/miapp/img/products/stm32f401.jpg",
                "datasheet_url": "https://www.st.com/resource/en/datasheet/stm32f401re.pdf",
                "encapsulado": "LQFP-64",
                "voltaje_operacion": "1.7V - 3.6V",
                "pines": 64,
                "especificaciones_tecnicas": {
                    "arquitectura": "ARM Cortex-M4 con FPU",
                    "frecuencia_reloj": "84 MHz",
                    "memoria_flash": "512 KB",
                    "memoria_sram": "96 KB",
                    "canales_adc": 16,
                    "resolucion_adc": "12-bit",
                    "interfaces_comunicacion": ["3x I2C", "3x USART", "4x SPI", "1x USB 2.0 OTG"],
                    "temporizadores": 8,
                },
                "precios_escalonados": [
                    PrecioEscalonado(cantidad_minima=10, precio_unitario=Decimal("112.00")),
                    PrecioEscalonado(cantidad_minima=50, precio_unitario=Decimal("98.50")),
                    PrecioEscalonado(cantidad_minima=250, precio_unitario=Decimal("84.00")),
                ],
                "stock_disponible": 350,
                "stock_reservado": 10,
                "ubicacion_anaquel": "Pasillo A, Gaveta 12-B",
                "stock_minimo_alerta": 25,
            },
            {
                "sku": "ESP32-WROOM-32D",
                "nombre": "Módulo SoC Wi-Fi + Bluetooth Dual-Core 240MHz",
                "categoria": cat_esp,
                "proveedor": proveedores_dict["ESPR"],
                "precio_base": Decimal("95.00"),
                "descripcion": "Módulo MCU inalámbrico altamente integrado con conectividad Wi-Fi 802.11 b/g/n y Bluetooth v4.2 BR/EDR y BLE. Incorpora procesador dual-core Xtensa de 32 bits.",
                "imagen_url": "/static/miapp/img/products/esp32.jpg",
                "datasheet_url": "https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32d_datasheet_en.pdf",
                "encapsulado": "SMD-38",
                "voltaje_operacion": "3.0V - 3.6V",
                "pines": 38,
                "especificaciones_tecnicas": {
                    "cpu": "Xtensa Dual-Core 32-bit LX6",
                    "frecuencia_reloj": "240 MHz",
                    "memoria_flash": "4 MB SPI Flash",
                    "memoria_sram": "520 KB",
                    "conectividad_wifi": "802.11 b/g/n (hasta 150 Mbps)",
                    "bluetooth": "v4.2 BR/EDR y BLE",
                    "antena": "PCB integrada",
                    "seguridad": ["WPA/WPA2/WPA3", "Acelerador criptográfico AES/SHA/RSA"],
                },
                "precios_escalonados": [
                    PrecioEscalonado(cantidad_minima=10, precio_unitario=Decimal("85.00")),
                    PrecioEscalonado(cantidad_minima=50, precio_unitario=Decimal("74.00")),
                    PrecioEscalonado(cantidad_minima=100, precio_unitario=Decimal("65.00")),
                ],
                "stock_disponible": 500,
                "stock_reservado": 25,
                "ubicacion_anaquel": "Pasillo A, Gaveta 08-A",
                "stock_minimo_alerta": 50,
            },
            {
                "sku": "ATMEGA328P-PU",
                "nombre": "MCU AVR 8-Bit 20MHz 32KB Flash DIP-28",
                "categoria": cat_avr,
                "proveedor": proveedores_dict["MCHP"],
                "precio_base": Decimal("78.00"),
                "descripcion": "El microcontrolador clásico de 8 bits utilizado en placas de desarrollo tipo Arduino Uno. Bajo consumo de energía con tecnología picoPower.",
                "imagen_url": "/static/miapp/img/products/atmega328p.jpg",
                "datasheet_url": "https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-7810-Automotive-Microcontrollers-ATmega328P_Datasheet.pdf",
                "encapsulado": "DIP-28",
                "voltaje_operacion": "1.8V - 5.5V",
                "pines": 28,
                "especificaciones_tecnicas": {
                    "arquitectura": "AVR RISC de 8 bits",
                    "frecuencia_reloj": "20 MHz",
                    "memoria_flash": "32 KB",
                    "memoria_sram": "2 KB",
                    "memoria_eeprom": "1 KB",
                    "pines_gpio": 23,
                    "canales_adc": 6,
                    "resolucion_adc": "10-bit",
                },
                "precios_escalonados": [
                    PrecioEscalonado(cantidad_minima=10, precio_unitario=Decimal("70.00")),
                    PrecioEscalonado(cantidad_minima=50, precio_unitario=Decimal("62.00")),
                    PrecioEscalonado(cantidad_minima=100, precio_unitario=Decimal("54.00")),
                ],
                "stock_disponible": 220,
                "stock_reservado": 0,
                "ubicacion_anaquel": "Pasillo A, Gaveta 05-C",
                "stock_minimo_alerta": 30,
            },
            {
                "sku": "DRV8825",
                "nombre": "Driver para Motor a Pasos Bipolar Micropasos 1/32",
                "categoria": cat_analog,
                "proveedor": proveedores_dict["TI"],
                "precio_base": Decimal("58.00"),
                "descripcion": "Controlador de motor a pasos bipolar con traductor incorporado para control mediante pines STEP/DIR. Soporta hasta 1/32 de micropasos para movimiento ultra suave.",
                "imagen_url": "/static/miapp/img/products/drv8825.jpg",
                "datasheet_url": "https://www.ti.com/lit/ds/symlink/drv8825.pdf",
                "encapsulado": "Módulo PCB / HTSSOP-28",
                "voltaje_operacion": "8.2V - 45V",
                "pines": 16,
                "especificaciones_tecnicas": {
                    "corriente_max": "2.5 A (con disipador de calor)",
                    "resolucion_pasos": ["Paso completo", "1/2", "1/4", "1/8", "1/16", "1/32"],
                    "protecciones": ["Sobrecorriente", "Cortocircuito", "Bloqueo por subtensión", "Sobrecalentamiento"],
                    "voltaje_logica": "3.3V - 5V compatible",
                },
                "precios_escalonados": [
                    PrecioEscalonado(cantidad_minima=10, precio_unitario=Decimal("52.00")),
                    PrecioEscalonado(cantidad_minima=50, precio_unitario=Decimal("45.00")),
                    PrecioEscalonado(cantidad_minima=100, precio_unitario=Decimal("39.00")),
                ],
                "stock_disponible": 180,
                "stock_reservado": 5,
                "ubicacion_anaquel": "Pasillo B, Gaveta 14-C",
                "stock_minimo_alerta": 20,
            },
            {
                "sku": "L298N-MOD",
                "nombre": "Módulo Driver Puente H Dual para Motores DC y Pasos",
                "categoria": cat_analog,
                "proveedor": proveedores_dict["ST"],
                "precio_base": Decimal("65.00"),
                "descripcion": "Módulo controlador de potencia con puente H doble basado en el circuito integrado L298N. Capaz de manejar 2 motores DC en ambos sentidos de giro o 1 motor a pasos de 4 fases.",
                "imagen_url": "/static/miapp/img/products/l298n.jpg",
                "datasheet_url": "https://www.st.com/resource/en/datasheet/l298.pdf",
                "encapsulado": "Módulo PCB con Disipador",
                "voltaje_operacion": "5V - 35V",
                "pines": 8,
                "especificaciones_tecnicas": {
                    "corriente_pico": "2 A por puente",
                    "potencia_max": "25 W",
                    "regulador_interno": "78M05 a bordo (5V lógico)",
                    "control_velocidad": "Señales PWM",
                },
                "precios_escalonados": [
                    PrecioEscalonado(cantidad_minima=5, precio_unitario=Decimal("58.00")),
                    PrecioEscalonado(cantidad_minima=20, precio_unitario=Decimal("50.00")),
                    PrecioEscalonado(cantidad_minima=50, precio_unitario=Decimal("42.00")),
                ],
                "stock_disponible": 140,
                "stock_reservado": 2,
                "ubicacion_anaquel": "Pasillo B, Gaveta 15-A",
                "stock_minimo_alerta": 15,
            },
            {
                "sku": "MPU-6050",
                "nombre": "Sensor Inercial IMU 6-DOF (Giroscopio + Acelerómetro)",
                "categoria": cat_sensores_inerciales,
                "proveedor": proveedores_dict["INVN"],
                "precio_base": Decimal("48.00"),
                "descripcion": "Sensor de movimiento de 6 grados de libertad que combina un giroscopio de 3 ejes y un acelerómetro de 3 ejes con procesador Digital Motion Processor (DMP) a bordo.",
                "imagen_url": "/static/miapp/img/products/mpu6050.jpg",
                "datasheet_url": "https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Datasheet1.pdf",
                "encapsulado": "QFN-24 / Módulo GY-521",
                "voltaje_operacion": "3.3V - 5V",
                "pines": 8,
                "especificaciones_tecnicas": {
                    "rango_giroscopio": "±250, ±500, ±1000, ±2000 °/s",
                    "rango_acelerometro": "±2g, ±4g, ±8g, ±16g",
                    "comunicacion": "Bus I2C hasta 400 kHz",
                    "adc_interno": "16-bit para cada eje",
                    "filtro_interno": "DMP (Digital Motion Processing)",
                },
                "precios_escalonados": [
                    PrecioEscalonado(cantidad_minima=10, precio_unitario=Decimal("42.00")),
                    PrecioEscalonado(cantidad_minima=50, precio_unitario=Decimal("36.00")),
                    PrecioEscalonado(cantidad_minima=100, precio_unitario=Decimal("30.00")),
                ],
                "stock_disponible": 300,
                "stock_reservado": 0,
                "ubicacion_anaquel": "Pasillo C, Gaveta 03-D",
                "stock_minimo_alerta": 40,
            },
            {
                "sku": "INA219",
                "nombre": "Monitor Bidireccional de Corriente y Potencia I2C",
                "categoria": cat_sensores_potencia,
                "proveedor": proveedores_dict["TI"],
                "precio_base": Decimal("72.00"),
                "descripcion": "Circuito integrado sensor de corriente shunt de lado alto con interfaz I2C. Mide caída de tensión en el shunt y voltaje del bus, calculando corriente y potencia automáticamente.",
                "imagen_url": "/static/miapp/img/products/ina219.jpg",
                "datasheet_url": "https://www.ti.com/lit/ds/symlink/ina219.pdf",
                "encapsulado": "SOT-23 / Módulo Breakout",
                "voltaje_operacion": "3.0V - 5.5V",
                "pines": 6,
                "especificaciones_tecnicas": {
                    "rango_tension_bus": "0V a 26V",
                    "precision_medicion": "1% de margen de error",
                    "resistencia_shunt": "0.1 ohm (1% 2W)",
                    "corriente_max_medible": "±3.2 A",
                    "interfaz": "I2C con 4 direcciones seleccionables",
                },
                "precios_escalonados": [
                    PrecioEscalonado(cantidad_minima=10, precio_unitario=Decimal("64.00")),
                    PrecioEscalonado(cantidad_minima=50, precio_unitario=Decimal("56.00")),
                    PrecioEscalonado(cantidad_minima=100, precio_unitario=Decimal("48.00")),
                ],
                "stock_disponible": 160,
                "stock_reservado": 0,
                "ubicacion_anaquel": "Pasillo C, Gaveta 06-B",
                "stock_minimo_alerta": 20,
            },
            {
                "sku": "NEMA17-17HS4401",
                "nombre": "Motor a Pasos Bipolar NEMA 17 40mm 1.7A 40N.cm",
                "categoria": cat_actuadores,
                "proveedor": proveedores_dict["STP"],
                "precio_base": Decimal("240.00"),
                "descripcion": "Motor a pasos híbrido bipolar de alta precisión para impresoras 3D, routers CNC, brazos robóticos y automatización mecatrónica. Alto torque y bajo calentamiento.",
                "imagen_url": "/static/miapp/img/products/nema17.jpg",
                "datasheet_url": "https://www.omc-stepperonline.com/download/17HS15-1704S.pdf",
                "encapsulado": "Carcasa NEMA 17 (42x42mm)",
                "voltaje_operacion": "12V - 36V",
                "pines": 4,
                "especificaciones_tecnicas": {
                    "angulo_paso": "1.8 grados (200 pasos/rev)",
                    "corriente_fase": "1.7 A",
                    "torque_retencion": "40 N.cm (56.7 oz.in)",
                    "longitud_cuerpo": "40 mm",
                    "diametro_eje": "5 mm (eje tipo D)",
                    "cables": "4 cables con conector JST-XH",
                },
                "precios_escalonados": [
                    PrecioEscalonado(cantidad_minima=5, precio_unitario=Decimal("215.00")),
                    PrecioEscalonado(cantidad_minima=20, precio_unitario=Decimal("190.00")),
                    PrecioEscalonado(cantidad_minima=50, precio_unitario=Decimal("168.00")),
                ],
                "stock_disponible": 75,
                "stock_reservado": 3,
                "ubicacion_anaquel": "Pasillo D, Estante 02-Inf",
                "stock_minimo_alerta": 10,
            },
        ]

        productos_dict = {}
        for pdata in productos_catalogo:
            stock_disp = pdata.pop("stock_disponible")
            stock_res = pdata.pop("stock_reservado")
            ubicacion = pdata.pop("ubicacion_anaquel")
            stock_min = pdata.pop("stock_minimo_alerta")

            prod, _ = Producto.objects.update_or_create(
                sku=pdata["sku"],
                defaults=pdata
            )
            productos_dict[prod.sku] = prod

            # ------------------------------------------------------------------
            # 5. INVENTARIO DE ALMACÉN (inventory) - Desacoplado 1:1
            # ------------------------------------------------------------------
            Inventario.objects.update_or_create(
                producto=prod,
                defaults={
                    "stock_disponible": stock_disp,
                    "stock_reservado": stock_res,
                    "ubicacion_anaquel": ubicacion,
                    "almacen": "Almacén Central Mecatrónica",
                    "stock_minimo_alerta": stock_min,
                }
            )

        self.stdout.write(self.style.SUCCESS(f"  [OK] {Producto.objects.count()} Productos registrados en catalogo."))
        self.stdout.write(self.style.SUCCESS(f"  [OK] {Inventario.objects.count()} Registros de Inventario fisico creados (desacoplados)."))

        # ----------------------------------------------------------------------
        # 6. ÓRDENES (orders) CON ITEMS EMBEBIDOS (DetalleVenta) Y PAGOS (payments)
        # ----------------------------------------------------------------------
        self.stdout.write("\n[5/6] Registrando ordenes con detalle embebido inmutable y pagos...")

        # Orden 1: Ingeniero Carlos Mendoza
        p_stm32 = productos_dict["STM32F401RET6"]
        p_l298n = productos_dict["L298N-MOD"]

        items_ord1 = [
            DetalleVenta(
                producto_id=str(p_stm32.id),
                sku=p_stm32.sku,
                nombre=p_stm32.nombre,
                encapsulado=p_stm32.encapsulado or "",
                cantidad=10,
                precio_unitario=Decimal("112.00"),  # Tarifa tier por 10 piezas
                subtotal=Decimal("1120.00"),
            ),
            DetalleVenta(
                producto_id=str(p_l298n.id),
                sku=p_l298n.sku,
                nombre=p_l298n.nombre,
                encapsulado=p_l298n.encapsulado or "",
                cantidad=2,
                precio_unitario=Decimal("65.00"),
                subtotal=Decimal("130.00"),
            ),
        ]
        subtotal_ord1 = Decimal("1250.00")
        envio_ord1 = Decimal("150.00")
        total_ord1 = Decimal("1400.00")

        ord1, _ = Orden.objects.update_or_create(
            folio="ORD-2026-008412",
            defaults={
                "usuario": usuarios_dict["cmendoza"],
                "estado": "pagada",
                "items": items_ord1,
                "subtotal": subtotal_ord1,
                "costo_envio": envio_ord1,
                "total": total_ord1,
                "direccion_entrega": usuarios_dict["cmendoza"].direccion_envio,
                "notas": "Entregar en laboratorio de mecatronica piso 4. Manejar con cuidado componentes electrostaticos.",
            }
        )

        Pago.objects.update_or_create(
            transaccion_id="ch_3N4y892xKL8721A001",
            defaults={
                "orden": ord1,
                "pasarela": "stripe",
                "monto": total_ord1,
                "moneda": "MXN",
                "estado": "aprobado",
                "datos_conciliacion": {
                    "charge_id": "ch_3N4y892xKL8721A001",
                    "payment_method": "pm_card_visa_ingenieria",
                    "auth_code": "STP-948210",
                    "receipt_url": "https://pay.stripe.com/receipts/008412",
                }
            }
        )

        # Orden 2: Mayorista ElectroMayoreo
        p_esp = productos_dict["ESP32-WROOM-32D"]
        p_drv = productos_dict["DRV8825"]

        items_ord2 = [
            DetalleVenta(
                producto_id=str(p_esp.id),
                sku=p_esp.sku,
                nombre=p_esp.nombre,
                encapsulado=p_esp.encapsulado or "",
                cantidad=100,
                precio_unitario=Decimal("65.00"),  # Tier mayorista >=100
                subtotal=Decimal("6500.00"),
            ),
            DetalleVenta(
                producto_id=str(p_drv.id),
                sku=p_drv.sku,
                nombre=p_drv.nombre,
                encapsulado=p_drv.encapsulado or "",
                cantidad=50,
                precio_unitario=Decimal("45.00"),  # Tier mayorista >=50
                subtotal=Decimal("2250.00"),
            ),
        ]
        subtotal_ord2 = Decimal("8750.00")
        envio_ord2 = Decimal("0.00")  # Envío gratis para mayoristas
        total_ord2 = Decimal("8750.00")

        ord2, _ = Orden.objects.update_or_create(
            folio="ORD-2026-008413",
            defaults={
                "usuario": usuarios_dict["electromayoreo"],
                "estado": "pagada",
                "items": items_ord2,
                "subtotal": subtotal_ord2,
                "costo_envio": envio_ord2,
                "total": total_ord2,
                "direccion_entrega": usuarios_dict["electromayoreo"].direccion_envio,
                "notas": "Pedido mayorista regular. Enviar factura con complemento de pago a facturacion@electromayoreo.com",
            }
        )

        Pago.objects.update_or_create(
            transaccion_id="SPEI-BBVA-20260320-99412",
            defaults={
                "orden": ord2,
                "pasarela": "transferencia",
                "monto": total_ord2,
                "moneda": "MXN",
                "estado": "aprobado",
                "datos_conciliacion": {
                    "banco_emisor": "BBVA Mexico",
                    "clabe_rastreo": "012180001234567890",
                    "referencia_numerica": "841320",
                    "concepto": "Pago mayoreo componentes",
                }
            }
        )

        # Orden 3: Venta mostrador POS en Caja
        p_mpu = productos_dict["MPU-6050"]
        p_ina = productos_dict["INA219"]

        items_ord3 = [
            DetalleVenta(
                producto_id=str(p_mpu.id),
                sku=p_mpu.sku,
                nombre=p_mpu.nombre,
                encapsulado=p_mpu.encapsulado or "",
                cantidad=2,
                precio_unitario=Decimal("48.00"),
                subtotal=Decimal("96.00"),
            ),
            DetalleVenta(
                producto_id=str(p_ina.id),
                sku=p_ina.sku,
                nombre=p_ina.nombre,
                encapsulado=p_ina.encapsulado or "",
                cantidad=1,
                precio_unitario=Decimal("72.00"),
                subtotal=Decimal("72.00"),
            ),
        ]
        subtotal_ord3 = Decimal("168.00")
        envio_ord3 = Decimal("0.00")
        total_ord3 = Decimal("168.00")

        ord3, _ = Orden.objects.update_or_create(
            folio="POS-20260320-A1B2",
            defaults={
                "usuario": usuarios_dict["cliente"],
                "estado": "pagada",
                "items": items_ord3,
                "subtotal": subtotal_ord3,
                "costo_envio": envio_ord3,
                "total": total_ord3,
                "direccion_entrega": usuarios_dict["cliente"].direccion_envio,
                "notas": "Venta en mostrador fisico POS operado por cajero.",
            }
        )

        Pago.objects.update_or_create(
            transaccion_id="TERM-POS-01-TX9932",
            defaults={
                "orden": ord3,
                "pasarela": "tarjeta",
                "monto": total_ord3,
                "moneda": "MXN",
                "estado": "aprobado",
                "datos_conciliacion": {
                    "terminal": "CAJA-POS-01",
                    "cajero": "cajero",
                    "marca_tarjeta": "Mastercard Debito",
                    "ultimos_4": "5521",
                    "autorizacion": "AUTH-481920",
                }
            }
        )

        # Orden 4: Orden en preparación
        p_nema = productos_dict["NEMA17-17HS4401"]
        items_ord4 = [
            DetalleVenta(
                producto_id=str(p_nema.id),
                sku=p_nema.sku,
                nombre=p_nema.nombre,
                encapsulado=p_nema.encapsulado or "",
                cantidad=4,
                precio_unitario=Decimal("240.00"),
                subtotal=Decimal("960.00"),
            ),
            DetalleVenta(
                producto_id=str(p_drv.id),
                sku=p_drv.sku,
                nombre=p_drv.nombre,
                encapsulado=p_drv.encapsulado or "",
                cantidad=4,
                precio_unitario=Decimal("58.00"),
                subtotal=Decimal("232.00"),
            ),
        ]
        subtotal_ord4 = Decimal("1192.00")
        envio_ord4 = Decimal("120.00")
        total_ord4 = Decimal("1312.00")

        ord4, _ = Orden.objects.update_or_create(
            folio="ORD-2026-008415",
            defaults={
                "usuario": usuarios_dict["cmendoza"],
                "estado": "preparando",
                "items": items_ord4,
                "subtotal": subtotal_ord4,
                "costo_envio": envio_ord4,
                "total": total_ord4,
                "direccion_entrega": usuarios_dict["cmendoza"].direccion_envio,
                "notas": "Kit mecatronico para proyecto de maquina CNC de 3 ejes.",
            }
        )

        Pago.objects.update_or_create(
            transaccion_id="PAYPAL-TX-99001428",
            defaults={
                "orden": ord4,
                "pasarela": "paypal",
                "monto": total_ord4,
                "moneda": "MXN",
                "estado": "aprobado",
                "datos_conciliacion": {
                    "paypal_order_id": "8XY991204KL",
                    "payer_email": "carlos.mendoza@robotech.mx",
                    "status": "COMPLETED",
                }
            }
        )

        self.stdout.write(self.style.SUCCESS(f"  [OK] {Orden.objects.count()} Ordenes de venta creadas con items embebidos."))
        self.stdout.write(self.style.SUCCESS(f"  [OK] {Pago.objects.count()} Transacciones de pago conciliadas."))

        self.stdout.write(self.style.HTTP_INFO("\n=================================================================="))
        self.stdout.write(self.style.SUCCESS("  CARGA DE INFORMACION EN MONGODB COMPLETADA CON EXITO!"))
        self.stdout.write(self.style.HTTP_INFO("=================================================================="))
        self.stdout.write(f"  - Categorias:    {Categoria.objects.count()}")
        self.stdout.write(f"  - Proveedores:   {Proveedor.objects.count()}")
        self.stdout.write(f"  - Usuarios/RBAC: {Usuario.objects.count()}")
        self.stdout.write(f"  - Productos:     {Producto.objects.count()}")
        self.stdout.write(f"  - Inventarios:   {Inventario.objects.count()}")
        self.stdout.write(f"  - Ordenes:       {Orden.objects.count()}")
        self.stdout.write(f"  - Pagos:         {Pago.objects.count()}")
        self.stdout.write(self.style.HTTP_INFO("==================================================================\n"))
