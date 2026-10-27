import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Polygon

def draw_uml():
    fig, ax = plt.subplots(figsize=(29, 23), dpi=300)
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')
    ax.set_xlim(0, 29)
    ax.set_ylim(0, 23)
    ax.axis('off')

    # Color palette
    COLOR_COLLECTION_HDR = '#1E3A8A'    # Deep Blue
    COLOR_COLLECTION_BG = '#FFFFFF'
    COLOR_COLLECTION_BORDER = '#2563EB'
    
    COLOR_EMBED_HDR = '#0F766E'         # Deep Teal
    COLOR_EMBED_BG = '#F0FDFA'
    COLOR_EMBED_BORDER = '#0D9488'
    
    COLOR_AUX_HDR = '#334155'           # Slate 700
    COLOR_AUX_BG = '#F8FAFC'
    COLOR_AUX_BORDER = '#64748B'

    COLOR_INV_HDR = '#B45309'           # Amber 700
    COLOR_INV_BG = '#FFFBEB'
    COLOR_INV_BORDER = '#D97706'

    # Title Banner
    ax.text(14.5, 22.2, "DIAGRAMA DE ARQUITECTURA UML: COLECCIONES Y MODELOS EMBEBIDOS", 
            fontsize=22, weight='bold', ha='center', va='center', color='#0F172A', fontname='DejaVu Sans')
    ax.text(14.5, 21.6, "Sistema de Gestión de Semiconductores y Mecatrónica | Django 6.1 + MongoDB (django-mongodb-backend)", 
            fontsize=13, style='italic', ha='center', va='center', color='#475569', fontname='DejaVu Sans')

    def draw_class_box(x, y, w, stereotype, title, subtitle, attributes, methods, header_bg, body_bg, border_color):
        header_h = 1.05
        attr_spacing = 0.30
        method_spacing = 0.28
        h_attrs = len(attributes) * attr_spacing
        h_methods = (len(methods) * method_spacing + 0.3) if methods else 0
        total_h = header_h + h_attrs + h_methods + 0.35

        # Main box
        box = FancyBboxPatch((x, y), w, total_h, boxstyle="round,pad=0.02,rounding_size=0.15",
                             facecolor=body_bg, edgecolor=border_color, linewidth=1.8, zorder=2)
        ax.add_patch(box)

        # Header compartment
        hdr_box = FancyBboxPatch((x, y + total_h - header_h), w, header_h, 
                                 boxstyle="round,pad=0.02,rounding_size=0.15",
                                 facecolor=header_bg, edgecolor=border_color, linewidth=1.5, zorder=3)
        ax.add_patch(hdr_box)

        # Header text
        ax.text(x + w/2, y + total_h - 0.25, stereotype, fontsize=8.5, weight='bold', 
                ha='center', va='center', color='#E2E8F0', fontname='DejaVu Sans', zorder=4)
        ax.text(x + w/2, y + total_h - 0.55, title, fontsize=12.5, weight='bold', 
                ha='center', va='center', color='#FFFFFF', fontname='DejaVu Sans', zorder=4)
        ax.text(x + w/2, y + total_h - 0.85, subtitle, fontsize=8.2, style='italic',
                ha='center', va='center', 
                color='#BAE6FD' if header_bg == COLOR_COLLECTION_HDR else ('#FEF08A' if header_bg == COLOR_INV_HDR else '#99F6E4'), 
                fontname='DejaVu Sans', zorder=4)

        # Attribute text
        cur_y = y + total_h - header_h - 0.24
        for attr in attributes:
            ax.text(x + 0.22, cur_y, attr, fontsize=8.6, ha='left', va='center', 
                    color='#1E293B', fontname='DejaVu Sans', zorder=4)
            cur_y -= attr_spacing

        # Methods
        if methods:
            ax.plot([x, x + w], [cur_y + 0.12, cur_y + 0.12], color=border_color, linestyle='--', linewidth=0.9, zorder=3)
            cur_y -= 0.18
            for m in methods:
                ax.text(x + 0.22, cur_y, m, fontsize=8.2, style='italic', ha='left', va='center', 
                        color='#0369A1' if header_bg == COLOR_COLLECTION_HDR else ('#9A3412' if header_bg == COLOR_INV_HDR else '#0F766E'), 
                        fontname='DejaVu Sans', zorder=4)
                cur_y -= method_spacing
                
        return total_h

    # ==========================
    # 1. Definición de Cajas en Grid 4x3 (Con amplios márgenes)
    # ==========================

    # --- FILA SUPERIOR (Top: y=15.0 - 15.2) ---
    # auth.User (x=1.0, y=15.2, w=5.0)
    h_auth = draw_class_box(
        x=1.0, y=15.2, w=5.0,
        stereotype="«Django Core Auth»",
        title="auth.User",
        subtitle="Colección de Cuentas Core",
        attributes=[
            "+ id : ObjectId / AutoField (PK)",
            "+ username : String (unique)",
            "+ password : HashString",
            "+ email : String",
            "+ is_staff : Boolean",
            "+ is_superuser : Boolean",
            "+ is_active : Boolean",
            "+ date_joined : ISODate"
        ],
        methods=[],
        header_bg=COLOR_AUX_HDR, body_bg=COLOR_AUX_BG, border_color=COLOR_AUX_BORDER
    )

    # Usuario (x=7.6, y=14.8, w=5.2) -> h ~ 5.4, top ~ 20.2
    h_user = draw_class_box(
        x=7.6, y=14.8, w=5.2,
        stereotype="«MongoDB Collection»",
        title="Usuario",
        subtitle="db_table: 'users'",
        attributes=[
            "+ _id : ObjectId (PK)",
            "+ user_id : ObjectId (1:1 FK auth.User)",
            "+ username : String (unique)",
            "+ email : String (unique)",
            "+ nombre_completo : String",
            "+ telefono : String",
            "+ rol : Enum [admin, cajero, cliente...]",
            "+ direccion_envio : Direccion",
            "+ direccion_facturacion : Direccion",
            "+ activo : Boolean",
            "+ creado_en : ISODate"
        ],
        methods=[
            "+ es_admin() : Boolean",
            "+ es_cajero() : Boolean"
        ],
        header_bg=COLOR_COLLECTION_HDR, body_bg=COLOR_COLLECTION_BG, border_color=COLOR_COLLECTION_BORDER
    )

    # Categoria (x=14.6, y=15.4, w=5.4) -> h ~ 4.2, top ~ 19.6
    h_cat = draw_class_box(
        x=14.6, y=15.4, w=5.4,
        stereotype="«MongoDB Collection»",
        title="Categoria",
        subtitle="db_table: 'categories'",
        attributes=[
            "+ _id : ObjectId (PK)",
            "+ nombre : String",
            "+ slug : String (unique)",
            "+ descripcion : String",
            "+ parent_id : ObjectId (FK self 1:N)",
            "+ activa : Boolean"
        ],
        methods=[
            "+ ruta_jerarquica() : String"
        ],
        header_bg=COLOR_COLLECTION_HDR, body_bg=COLOR_COLLECTION_BG, border_color=COLOR_COLLECTION_BORDER
    )

    # Proveedor (x=21.8, y=15.0, w=5.8) -> h ~ 4.6, top ~ 19.6
    h_prov = draw_class_box(
        x=21.8, y=15.0, w=5.8,
        stereotype="«MongoDB Collection»",
        title="Proveedor",
        subtitle="db_table: 'suppliers' (Anexa)",
        attributes=[
            "+ _id : ObjectId (PK)",
            "+ nombre : String",
            "+ codigo : String (unique, e.g. TI, ST)",
            "+ sitio_web : URLString",
            "+ email_contacto : String",
            "+ telefono : String",
            "+ pais : String (default: México)",
            "+ lineas_componentes : String",
            "+ activo : Boolean",
            "+ creado_en : ISODate"
        ],
        methods=[
            "+ __str__() : Nombre y Código"
        ],
        header_bg=COLOR_COLLECTION_HDR, body_bg=COLOR_COLLECTION_BG, border_color=COLOR_COLLECTION_BORDER
    )

    # --- FILA MEDIA (Mid: y=7.8 - 8.2) ---
    # Direccion (x=1.0, y=8.0, w=5.0) -> h ~ 4.2, top ~ 12.2
    h_dir = draw_class_box(
        x=1.0, y=8.0, w=5.0,
        stereotype="«Embedded Document»",
        title="Direccion",
        subtitle="Subdocumento Embebido (MongoDB)",
        attributes=[
            "+ calle : String",
            "+ colonia : String",
            "+ ciudad : String",
            "+ estado : String",
            "+ codigo_postal : String",
            "+ pais : String (default: México)",
            "+ referencias : String"
        ],
        methods=[
            "+ __str__() : Formato Dirección Completa"
        ],
        header_bg=COLOR_EMBED_HDR, body_bg=COLOR_EMBED_BG, border_color=COLOR_EMBED_BORDER
    )

    # Orden (x=7.6, y=7.6, w=5.2) -> h ~ 5.6, top ~ 13.2 (bottom of Usuario is 14.8 -> gap 1.6!)
    h_ord = draw_class_box(
        x=7.6, y=7.6, w=5.2,
        stereotype="«MongoDB Collection»",
        title="Orden",
        subtitle="db_table: 'orders'",
        attributes=[
            "+ _id : ObjectId (PK)",
            "+ folio : String (unique)",
            "+ usuario_id : ObjectId (FK -> users)",
            "+ estado : Enum [pendiente, pagada...]",
            "+ items : Array[DetalleVenta]",
            "+ subtotal : Decimal128",
            "+ costo_envio : Decimal128",
            "+ total : Decimal128",
            "+ direccion_entrega : Direccion",
            "+ notas : String",
            "+ creado_en : ISODate",
            "+ actualizado_en : ISODate"
        ],
        methods=[
            "+ __str__() : Folio, Total y Estado"
        ],
        header_bg=COLOR_COLLECTION_HDR, body_bg=COLOR_COLLECTION_BG, border_color=COLOR_COLLECTION_BORDER
    )

    # Producto (x=14.6, y=7.4, w=5.8) -> h ~ 6.3, top ~ 13.7 (bottom of Categoria is 15.4 -> gap 1.7!)
    h_prod = draw_class_box(
        x=14.6, y=7.4, w=5.8,
        stereotype="«MongoDB Collection»",
        title="Producto",
        subtitle="db_table: 'products'",
        attributes=[
            "+ _id : ObjectId (PK)",
            "+ sku : String (unique, MPN)",
            "+ nombre : String",
            "+ categoria_id : ObjectId (FK -> categories)",
            "+ proveedor_id : ObjectId (FK -> suppliers)",
            "+ precio_base : Decimal128",
            "+ descripcion : String",
            "+ datasheet_url : URLString",
            "+ encapsulado : String (e.g. LQFP-64)",
            "+ voltaje_operacion : String",
            "+ pines : Integer",
            "+ especificaciones_tecnicas : JSON",
            "+ precios_escalonados : Array[PrecioEscalonado]",
            "+ activo : Boolean",
            "+ creado_en : ISODate",
            "+ actualizado_en : ISODate"
        ],
        methods=[
            "+ __str__() : SKU y Nombre"
        ],
        header_bg=COLOR_COLLECTION_HDR, body_bg=COLOR_COLLECTION_BG, border_color=COLOR_COLLECTION_BORDER
    )

    # PrecioEscalonado (x=21.8, y=9.2, w=5.8) -> h ~ 2.6
    h_tier = draw_class_box(
        x=21.8, y=9.2, w=5.8,
        stereotype="«Embedded Document»",
        title="PrecioEscalonado",
        subtitle="Subdocumento Embebido (Tiers)",
        attributes=[
            "+ cantidad_minima : PositiveInt (Desde)",
            "+ precio_unitario : Decimal128 ($)"
        ],
        methods=[
            "+ __str__() : Resumen Rango de Precio"
        ],
        header_bg=COLOR_EMBED_HDR, body_bg=COLOR_EMBED_BG, border_color=COLOR_EMBED_BORDER
    )

    # --- FILA INFERIOR (Bottom: y=1.0) ---
    # DetalleVenta (x=1.0, y=1.0, w=5.0) -> h ~ 4.2
    h_det = draw_class_box(
        x=1.0, y=1.0, w=5.0,
        stereotype="«Embedded Document»",
        title="DetalleVenta",
        subtitle="Instantánea / Snapshot de Venta",
        attributes=[
            "+ producto_id : String",
            "+ sku : String",
            "+ nombre : String",
            "+ encapsulado : String",
            "+ cantidad : PositiveInt",
            "+ precio_unitario : Decimal128",
            "+ subtotal : Decimal128"
        ],
        methods=[
            "+ __str__() : Resumen de Item Vendido"
        ],
        header_bg=COLOR_EMBED_HDR, body_bg=COLOR_EMBED_BG, border_color=COLOR_EMBED_BORDER
    )

    # Pago (x=7.6, y=1.0, w=5.2) -> h ~ 4.6 (top ~ 5.6, bottom of Orden is 7.6 -> gap 2.0!)
    h_pago = draw_class_box(
        x=7.6, y=1.0, w=5.2,
        stereotype="«MongoDB Collection»",
        title="Pago",
        subtitle="db_table: 'payments' (Anexa)",
        attributes=[
            "+ _id : ObjectId (PK)",
            "+ orden_id : ObjectId (FK -> orders)",
            "+ pasarela : Enum [stripe, paypal...]",
            "+ transaccion_id : String (unique)",
            "+ monto : Decimal128",
            "+ moneda : String (default: MXN)",
            "+ estado : Enum [aprobado, pendiente..]",
            "+ datos_conciliacion : JSON / Object",
            "+ fecha_transaccion : ISODate"
        ],
        methods=[
            "+ __str__() : Pasarela y Monto"
        ],
        header_bg=COLOR_COLLECTION_HDR, body_bg=COLOR_COLLECTION_BG, border_color=COLOR_COLLECTION_BORDER
    )

    # Inventario (x=14.6, y=1.0, w=5.8) -> h ~ 4.9 (top ~ 5.9, bottom of Producto is 7.4 -> gap 1.5!)
    h_inv = draw_class_box(
        x=14.6, y=1.0, w=5.8,
        stereotype="«MongoDB Collection»",
        title="Inventario",
        subtitle="db_table: 'inventory' (Desacoplado)",
        attributes=[
            "+ _id : ObjectId (PK)",
            "+ producto_id : ObjectId (1:1 Unique FK)",
            "+ stock_disponible : PositiveInt",
            "+ stock_reservado : PositiveInt",
            "+ ubicacion_anaquel : String",
            "+ almacen : String",
            "+ stock_minimo_alerta : PositiveInt",
            "+ actualizado_en : ISODate"
        ],
        methods=[
            "+ stock_total : Property",
            "+ reservar(cantidad) : Boolean",
            "+ liberar_reserva(cantidad) : Void",
            "+ confirmar_venta(cantidad) : Void",
            "+ descontar_venta_directa(cant) : Boolean"
        ],
        header_bg=COLOR_INV_HDR, body_bg=COLOR_INV_BG, border_color=COLOR_INV_BORDER
    )

    # Leyenda (x=21.8, y=1.0, w=5.8, h=6.5)
    leg_x = 21.8
    leg_y = 1.0
    leg_w = 5.8
    leg_h = 6.6
    leg_box = FancyBboxPatch((leg_x, leg_y), leg_w, leg_h, boxstyle="round,pad=0.02,rounding_size=0.15",
                             facecolor='#FFFFFF', edgecolor='#64748B', linewidth=1.5, zorder=2)
    ax.add_patch(leg_box)
    
    leg_hdr = FancyBboxPatch((leg_x, leg_y + leg_h - 0.75), leg_w, 0.75, 
                             boxstyle="round,pad=0.02,rounding_size=0.15",
                             facecolor='#0F172A', edgecolor='#64748B', linewidth=1.2, zorder=3)
    ax.add_patch(leg_hdr)
    ax.text(leg_x + leg_w/2, leg_y + leg_h - 0.38, "CONVENCIONES Y LEYENDA ARQUITECTÓNICA", 
            fontsize=9.2, weight='bold', ha='center', va='center', color='#FFFFFF', fontname='DejaVu Sans', zorder=4)

    items = [
        ("Colección Raíz MongoDB (Colección en BSON)", COLOR_COLLECTION_HDR, 'square'),
        ("Subdocumento Embebido (EmbeddedModel MongoDB)", COLOR_EMBED_HDR, 'square'),
        ("Inventario Desacoplado (Alta Concurrencia)", COLOR_INV_HDR, 'square'),
        ("Modelo Base de Autenticación Django", COLOR_AUX_HDR, 'square'),
        ("Relación 1:1 por Referencia (OneToOneField / ObjectId)", '#1E3A8A', 'line_1_1'),
        ("Relación 1:N por Referencia (ForeignKey / ObjectId)", '#1E3A8A', 'line_1_n'),
        ("Composición / Embebido (EmbeddedModel / Array)", '#0D9488', 'embed'),
    ]

    ly = leg_y + leg_h - 1.30
    for text, col, kind in items:
        if kind == 'square':
            rect = patches.Rectangle((leg_x + 0.35, ly - 0.12), 0.34, 0.25, facecolor=col, edgecolor=col, zorder=4)
            ax.add_patch(rect)
        elif kind == 'line_1_1':
            ax.plot([leg_x + 0.3, leg_x + 0.8], [ly, ly], color=col, lw=2.2, zorder=4)
            ax.plot(leg_x + 0.8, ly, marker='>', color=col, markersize=5, zorder=4)
            ax.text(leg_x + 0.55, ly + 0.12, "1:1", fontsize=7.5, weight='bold', color=col, ha='center', zorder=5)
        elif kind == 'line_1_n':
            ax.plot([leg_x + 0.3, leg_x + 0.8], [ly, ly], color=col, lw=2.2, zorder=4)
            ax.plot(leg_x + 0.8, ly, marker='>', color=col, markersize=5, zorder=4)
            ax.text(leg_x + 0.55, ly + 0.12, "1:N", fontsize=7.5, weight='bold', color=col, ha='center', zorder=5)
        elif kind == 'embed':
            diamond = Polygon([
                (leg_x + 0.38, ly), (leg_x + 0.47, ly + 0.1), (leg_x + 0.56, ly), (leg_x + 0.47, ly - 0.1)
            ], closed=True, facecolor=col, edgecolor='#0F766E', zorder=4)
            ax.add_patch(diamond)
            ax.plot([leg_x + 0.56, leg_x + 0.8], [ly, ly], color=col, lw=1.8, linestyle='--', zorder=4)

        ax.text(leg_x + 0.95, ly, text, fontsize=8.2, ha='left', va='center', color='#334155', fontname='DejaVu Sans', zorder=4)
        ly -= 0.65

    # ==========================
    # 2. Conectores y Relaciones (Sin Colisiones)
    # ==========================

    def draw_ref_arrow(p1, p2, label="", mult1="", mult2="", color="#1E3A8A", rad=0.0, label_offset=(0, 0), m1_offset=(0.15, 0.2), m2_offset=(-0.45, 0.2)):
        ax.annotate(
            "", xy=p2, xytext=p1,
            arrowprops=dict(
                arrowstyle="-|>", color=color, lw=2.0,
                connectionstyle=f"arc3,rad={rad}" if rad != 0 else "arc3"
            ),
            zorder=5
        )
        mx = (p1[0] + p2[0]) / 2 + label_offset[0]
        my = (p1[1] + p2[1]) / 2 + label_offset[1]
        if label:
            ax.text(mx, my, label, fontsize=8.2, weight='bold', color=color, 
                    ha='center', va='center', bbox=dict(boxstyle="round,pad=0.2", fc="#FFFFFF", ec=color, lw=0.8), zorder=6)
        if mult1:
            ax.text(p1[0] + m1_offset[0], p1[1] + m1_offset[1], mult1, fontsize=9.2, weight='bold', color='#0F172A', zorder=6)
        if mult2:
            ax.text(p2[0] + m2_offset[0], p2[1] + m2_offset[1], mult2, fontsize=9.2, weight='bold', color='#0F172A', zorder=6)

    def draw_embed_arrow(p_cont, p_emb, label="", mult="1..*", rad=0.0, label_offset=(0, 0), direction='left'):
        dx = 0.20
        dy = 0.14
        if direction == 'left':
            diamond = Polygon([
                (p_cont[0], p_cont[1]),
                (p_cont[0] - dx, p_cont[1] + dy),
                (p_cont[0] - 2*dx, p_cont[1]),
                (p_cont[0] - dx, p_cont[1] - dy)
            ], closed=True, facecolor='#0D9488', edgecolor='#0F766E', zorder=7)
            start_pt = (p_cont[0] - 2*dx, p_cont[1])
            m_pos = (p_emb[0] + 0.15, p_emb[1] + 0.22)
        else: # right
            diamond = Polygon([
                (p_cont[0], p_cont[1]),
                (p_cont[0] + dx, p_cont[1] + dy),
                (p_cont[0] + 2*dx, p_cont[1]),
                (p_cont[0] + dx, p_cont[1] - dy)
            ], closed=True, facecolor='#0D9488', edgecolor='#0F766E', zorder=7)
            start_pt = (p_cont[0] + 2*dx, p_cont[1])
            m_pos = (p_emb[0] - 0.45, p_emb[1] + 0.22)

        ax.add_patch(diamond)

        ax.annotate(
            "", xy=p_emb, xytext=start_pt,
            arrowprops=dict(
                arrowstyle="-|>", color="#0D9488", lw=2.0, linestyle="--",
                connectionstyle=f"arc3,rad={rad}" if rad != 0 else "arc3"
            ),
            zorder=5
        )
        mx = (p_cont[0] + p_emb[0]) / 2 + label_offset[0]
        my = (p_cont[1] + p_emb[1]) / 2 + label_offset[1]
        if label:
            ax.text(mx, my, label, fontsize=8.2, weight='bold', color='#0F766E',
                    ha='center', va='center', bbox=dict(boxstyle="round,pad=0.2", fc="#F0FDFA", ec="#0D9488", lw=0.8), zorder=6)
        ax.text(m_pos[0], m_pos[1], mult, fontsize=9.2, weight='bold', color='#0F766E', zorder=6)

    # 1. auth.User <--> Usuario (1:1)
    draw_ref_arrow((6.0, 17.0), (7.6, 17.0), label="1:1 Perfil Extendido", mult1="1", mult2="0..1", color="#334155",
                   m1_offset=(0.15, 0.2), m2_offset=(-0.50, 0.2))

    # 2. Usuario --> Direccion (1:1 Embebido para envío y facturación)
    draw_embed_arrow((7.6, 15.6), (6.0, 11.4), label="«embeds 1:1» (envío / fact)", mult="1..2", rad=0.06, label_offset=(-0.15, 0.12), direction='left')

    # 3. Usuario --> Orden (1:N Referenciado)
    # Usuario bottom = 14.8, Orden top = 13.2 -> midpoint = 14.0
    draw_ref_arrow((10.2, 14.8), (10.2, 13.2), label="1:N Órdenes Cliente", mult1="1", mult2="0..*", color="#1E3A8A",
                   m1_offset=(0.15, -0.4), m2_offset=(0.15, 0.2))

    # 4. Orden --> Direccion (1:1 Embebido instantánea de entrega)
    draw_embed_arrow((7.6, 10.4), (6.0, 10.0), label="«embeds 1:1» (entrega)", mult="0..1", rad=-0.04, label_offset=(-0.05, 0.25), direction='left')

    # 5. Orden --> DetalleVenta (1:N Array Embebido items)
    draw_embed_arrow((7.6, 8.4), (6.0, 4.2), label="«embeds 1:N» (items snapshot)", mult="1..*", rad=0.08, label_offset=(-0.15, 0.12), direction='left')

    # 6. Orden --> Pago (1:N Referenciado)
    # Orden bottom = 7.6, Pago top = 5.6 -> midpoint = 6.6
    draw_ref_arrow((10.2, 7.6), (10.2, 5.6), label="1:N Pagos Registrados", mult1="1", mult2="0..*", color="#1E3A8A",
                   m1_offset=(0.15, -0.4), m2_offset=(0.15, 0.2))

    # 7. Categoria --> Categoria (1:N Jerarquía Autorreferencial)
    ax.annotate(
        "", xy=(17.8, 19.6), xytext=(16.6, 19.6),
        arrowprops=dict(arrowstyle="-|>", color="#1E3A8A", lw=2.0, connectionstyle="arc,angleA=90,angleB=90,armA=32,armB=32,rad=10"),
        zorder=5
    )
    ax.text(17.2, 20.35, "1:N Jerarquía (parent_id)", fontsize=8.2, weight='bold', color="#1E3A8A",
            ha='center', va='center', bbox=dict(boxstyle="round,pad=0.18", fc="#FFFFFF", ec="#1E3A8A", lw=0.8), zorder=6)

    # 8. Categoria --> Producto (1:N Referenciado)
    # Categoria bottom = 15.4, Producto top = 13.7 -> midpoint = 14.55
    draw_ref_arrow((17.5, 15.4), (17.5, 13.7), label="1:N Categorización", mult1="1", mult2="0..*", color="#1E3A8A",
                   m1_offset=(0.15, -0.4), m2_offset=(0.15, 0.2))

    # 9. Proveedor --> Producto (1:N Referenciado)
    draw_ref_arrow((21.8, 16.5), (20.4, 12.2), label="1:N Suministro Fabricante", mult1="1", mult2="0..*", color="#1E3A8A", rad=0.06, label_offset=(0.1, 0.1),
                   m1_offset=(-0.4, 0.2), m2_offset=(0.15, 0.2))

    # 10. Producto --> PrecioEscalonado (1:N Array Embebido)
    draw_embed_arrow((20.4, 10.5), (21.8, 10.5), label="«embeds 1:N» (tiers)", mult="0..*", rad=0.0, label_offset=(0, 0.25), direction='right')

    # 11. Producto <--> Inventario (1:1 Referenciado - Desacoplado)
    # Producto bottom = 7.4, Inventario top = 5.9 -> midpoint = 6.65
    draw_ref_arrow((17.5, 7.4), (17.5, 5.9), label="1:1 Stock Desacoplado", mult1="1", mult2="1", color="#B45309",
                   m1_offset=(0.15, -0.4), m2_offset=(0.15, 0.2))

    plt.tight_layout()
    output_path = "uml_colecciones_mongodb.png"
    plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"Diagram successfully saved to {output_path}")

if __name__ == "__main__":
    draw_uml()
