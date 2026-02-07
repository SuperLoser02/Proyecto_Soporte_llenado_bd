import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import date, timedelta
from collections import defaultdict
import pyodbc
from sqlalchemy import create_engine

# Configuración de conexión
server = 'localhost'
database = 'PROYECTO'  # Corregí el typo en el nombre

fk = Faker()

fecha_inicio = date(2024, 2, 5)
fecha_fin = date(2026, 2, 6)

#! SUCURSAL
cant_sucursales = 3
sucursal = ['Norte', 'Sur', 'Centro']
dict_sucursal = {
    'idSucursal': [i for i in range(1, cant_sucursales+1)],
    'nombre': [f"TecnoComp_{sucursal[i]}" for i in range(cant_sucursales)],
    'direccion': [fk.street_address() for _ in range(cant_sucursales)],
    'telefono': [str(random.randint(60000000, 79999999)) for _ in range(cant_sucursales)],
    'ubicacion': [fk.address().replace('\n', ', ') for _ in range(cant_sucursales)],
    'activa': [1 for _ in range(cant_sucursales)],
}
df_sucursal = pd.DataFrame(dict_sucursal)

#! ALMACEN
dict_Almacen = {
    'idAlmacen': [1, 2, 3],
    'idSucursal': [3, 1, 2],
    'descripcion': [fk.sentence(nb_words=6) for _ in range(3)],
}
df_Almacen = pd.DataFrame(dict_Almacen)

#! MarcaProducto
dict_MarcaProducto = {
    'idMarca': range(1, 15),
    'nombre': ['Samsung', 'Apple', 'LG', 'BOE', 'Xiaomi', 'Huawei', 'Motorola', 'Genérico', 'Kingston', 'Crucial', 'Western Digital', 'Seagate', 'OEM', 'Compatible'],
    'descripcion': [' '.join(fk.words(15)) for _ in range(14)],
}
df_MarcaProducto = pd.DataFrame(dict_MarcaProducto)

#! ModeloProducto
dict_ModeloProducto = {
    'idModelo': [i for i in range(1, 49)],
    'idMarca': [
        1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 13, 14, 14, 14
    ],
    'nombre': [
        'Pantalla', 'Batería', 'Cargador',
        'Pantalla', 'Batería', 'Cargador',
        'Pantalla', 'Batería',
        'Pantalla', 'Batería',
        'Pantalla', 'Batería', 'Cargador',
        'Pantalla', 'Batería', 'Cargador',
        'Pantalla', 'Batería', 'Cargador',
        'Pantalla', 'Batería', 'Teclado', 'Touchpad', 'Ventilador', 'Bisagra',
        'Puerto', 'Flex', 'Cámara', 'Cargador', 'Cable', 'Memoria RAM',
        'Memoria RAM', 'Almacenamiento', 'Cable',
        'Memoria RAM', 'Almacenamiento',
        'Almacenamiento', 'Cable', 'Cargador',
        'Almacenamiento', 'Cable',
        'Cargador', 'Cable', 'Batería', 'Pantalla',
        'Pantalla', 'Batería', 'Cargador'
    ],
    'descripcion': [' '.join(fk.words(15)) for _ in range(48)],
}
df_ModeloProducto = pd.DataFrame(dict_ModeloProducto)

#! producto
productos = []
id_producto = 1

def generar_codigo(marca, modelo, numero):
    marca_codigo = marca[:3].upper()
    modelo_codigo = modelo[:3].upper()
    return f"{marca_codigo}-{modelo_codigo}-{numero:04d}"

for idx, modelo_row in df_ModeloProducto.iterrows():
    id_modelo = modelo_row['idModelo']
    id_marca = modelo_row['idMarca']
    tipo_modelo = modelo_row['nombre']
    nombre_marca = df_MarcaProducto[df_MarcaProducto['idMarca'] == id_marca]['nombre'].values[0]
    
    if tipo_modelo == 'Pantalla':
        variaciones = [
            ('5.5"', 'Pantalla LCD 5.5 pulgadas', 450, 320, 'Unitario'),
            ('6.1"', 'Pantalla AMOLED 6.1 pulgadas', 850, 600, 'Unitario'),
            ('6.7"', 'Pantalla OLED 6.7 pulgadas', 1200, 850, 'Unitario'),
            ('14"', 'Pantalla LCD 14 pulgadas FHD', 520, 380, 'Unitario'),
            ('15.6"', 'Pantalla LCD 15.6 pulgadas FHD', 580, 420, 'Unitario'),
        ]
    elif tipo_modelo == 'Batería':
        variaciones = [
            ('3000mAh', 'Batería 3000mAh', 150, 100, 'Unitario'),
            ('4000mAh', 'Batería 4000mAh', 180, 120, 'Unitario'),
            ('5000mAh', 'Batería 5000mAh', 220, 150, 'Unitario'),
        ]
    elif tipo_modelo == 'Cargador':
        variaciones = [
            ('20W', 'Cargador 20W USB-C', 80, 50, 'Unitario'),
            ('45W', 'Cargador 45W USB-C', 120, 80, 'Unitario'),
            ('65W', 'Cargador 65W USB-C', 150, 100, 'Unitario'),
        ]
    elif tipo_modelo == 'Teclado':
        variaciones = [
            ('Español', 'Teclado Español', 120, 80, 'Unitario'),
            ('Inglés', 'Teclado Inglés', 110, 75, 'Unitario'),
        ]
    elif tipo_modelo == 'Touchpad':
        variaciones = [
            ('Universal', 'Touchpad Universal', 80, 55, 'Unitario'),
        ]
    elif tipo_modelo == 'Ventilador':
        variaciones = [
            ('Cooler', 'Ventilador Cooler', 45, 30, 'Unitario'),
        ]
    elif tipo_modelo == 'Bisagra':
        variaciones = [
            ('Derecha', 'Bisagra Derecha', 35, 20, 'Unitario'),
            ('Izquierda', 'Bisagra Izquierda', 35, 20, 'Unitario'),
        ]
    elif tipo_modelo == 'Puerto':
        variaciones = [
            ('USB-C', 'Puerto USB-C', 25, 15, 'Unitario'),
            ('HDMI', 'Puerto HDMI', 30, 18, 'Unitario'),
            ('USB 3.0', 'Puerto USB 3.0', 20, 12, 'Unitario'),
        ]
    elif tipo_modelo == 'Flex':
        variaciones = [
            ('Carga', 'Flex de Carga', 40, 25, 'Unitario'),
        ]
    elif tipo_modelo == 'Cámara':
        variaciones = [
            ('Frontal 8MP', 'Cámara Frontal 8MP', 60, 40, 'Unitario'),
            ('Trasera 48MP', 'Cámara Trasera 48MP', 95, 65, 'Unitario'),
        ]
    elif tipo_modelo == 'Cable':
        variaciones = [
            ('USB-C 1m', 'Cable USB-C 1 metro', 35, 20, 'Unitario'),
            ('Lightning 1m', 'Cable Lightning 1 metro', 45, 28, 'Unitario'),
        ]
    elif tipo_modelo == 'Memoria RAM':
        variaciones = [
            ('DDR4 8GB', 'Memoria RAM DDR4 8GB', 280, 200, 'Unitario'),
            ('DDR4 16GB', 'Memoria RAM DDR4 16GB', 520, 380, 'Unitario'),
            ('DDR5 16GB', 'Memoria RAM DDR5 16GB', 680, 500, 'Unitario'),
        ]
    elif tipo_modelo == 'Almacenamiento':
        variaciones = [
            ('SSD 240GB', 'SSD 240GB', 320, 230, 'Unitario'),
            ('SSD 480GB', 'SSD 480GB', 580, 420, 'Unitario'),
            ('HDD 1TB', 'HDD 1TB', 420, 300, 'Unitario'),
        ]
    else:
        variaciones = [
            ('Estándar', f'{tipo_modelo} Estándar', 100, 70, 'Unitario'),
        ]
    
    for var_nombre, descripcion, precio, costo, tipo_precio in variaciones:
        codigo = generar_codigo(nombre_marca, tipo_modelo, id_producto)
        nombre_completo = f"{nombre_marca} {tipo_modelo} {var_nombre}"
        
        productos.append({
            'IdProducto': id_producto,
            'IdMarca': id_marca,
            'IdModelo': id_modelo,
            'Codigo': codigo,
            'Nombre': nombre_completo,
            'Descripcion': descripcion,
            'PrecioVenta': precio,
            'CostoRef': costo,
            'TipoPrecio': tipo_precio
        })
        
        id_producto += 1

dict_Producto = {
    'idProducto': [p['IdProducto'] for p in productos],
    'idMarca': [p['IdMarca'] for p in productos],
    'idModelo': [p['IdModelo'] for p in productos],
    'codigo': [p['Codigo'] for p in productos],
    'nombre': [p['Nombre'] for p in productos],
    'descripcion': [p['Descripcion'] for p in productos],
    'precioVenta': [p['PrecioVenta'] for p in productos],
    'costoRef': [p['CostoRef'] for p in productos],
    'tipoPrecio': [p['TipoPrecio'] for p in productos],
}
df_Producto = pd.DataFrame(dict_Producto)

#! PROVEEDOR
cant_proveedor = 23
dict_Proveedor = {
    'idProveedor': range(1, cant_proveedor+1),
    'razonSocial': [fk.company() for _ in range(cant_proveedor)],
    'nit': [fk.bothify(text='########-#') for _ in range(cant_proveedor)],
    'telefono': [str(random.randint(60000000, 79999999)) for _ in range(cant_proveedor)],
    'direccion': [fk.address().replace('\n', ', ') for _ in range(cant_proveedor)],
    'email': [fk.company_email() for _ in range(cant_proveedor)],
    'activo': ['ACTIVO' if random.random() > 0.05 else 'NO ACTIVO' for _ in range(cant_proveedor)],
}
df_Proveedor = pd.DataFrame(dict_Proveedor)

#! EMPLEADO
cant_empleados = 33
lista_cargos = random.choices(
    ['Tecnico', 'Vendedor', 'Administrador', 'Gerente'],
    weights=[60, 25, 10, 5],
    k=cant_empleados
)
dict_empleados = {
    'idEmpleado': [i for i in range(1, cant_empleados+1)],
    'nombre': [fk.first_name() for _ in range(cant_empleados)],
    'apellidoP': [fk.last_name() for _ in range(cant_empleados)],
    'apellidoM': [fk.last_name() for _ in range(cant_empleados)],
    'telefono': [str(random.randint(60000000, 79999999)) for _ in range(cant_empleados)],
    'cargo': [lista_cargos[i] for i in range(cant_empleados)],
    'direccion': [fk.address().replace('\n', ', ') for _ in range(cant_empleados)],
    'email': [fk.email() for _ in range(cant_empleados)],
    'activo': ['ACTIVO' if random.random() > 0.05 else 'NO ACTIVO' for _ in range(cant_empleados)],
}
df_empleado = pd.DataFrame(dict_empleados)

#! GASTOS
cant_gastos = random.randint(20, 70)
fecha_Gastos = []
for _ in range(cant_gastos):
    d = fk.date_between(fecha_inicio, fecha_fin)
    while d.weekday() >= 5:
        d = fk.date_between(fecha_inicio, fecha_fin)
    fecha_Gastos.append(d)

dict_Gasto = {
    'idGasto': range(1, cant_gastos+1),
    'idSucursal': [random.randint(1, 3) for _ in range(cant_gastos)],
    'idEmpleado': [df_empleado.sample(1).iloc[0]['idEmpleado'] for _ in range(cant_gastos)],
    'fecha': fecha_Gastos,
    'concepto': ['Compras varias' for _ in range(cant_gastos)],
    'monto': [round(random.uniform(10, 120), 2) for _ in range(cant_gastos)],
    'comprobante': [f"COMP-{random.randint(1000, 9999)}" for _ in range(cant_gastos)]
}
df_Gasto = pd.DataFrame(dict_Gasto)

#! COMPRA (sin total aún)
cant_compra = 800
fecha_compra = []
for _ in range(cant_compra):
    d = fk.date_between(fecha_inicio, fecha_fin)
    while d.weekday() >= 5:
        d = fk.date_between(fecha_inicio, fecha_fin)
    fecha_compra.append(d)

dict_compra = {
    'idCompra': range(1, cant_compra+1),
    'idProveedor': [df_Proveedor.sample(1).iloc[0]['idProveedor'] for _ in range(cant_compra)],
    'idEmpleado': [df_empleado.sample(1).iloc[0]['idEmpleado'] for _ in range(cant_compra)],
    'idSucursal': [random.randint(1, cant_sucursales) for _ in range(cant_compra)],
    'fecha': fecha_compra,
    'total': [0.0 for _ in range(cant_compra)],  # Se calculará después
    'estado': ['completado' for _ in range(cant_compra)],
}

#! TIPO MOVIMIENTO INVENTARIO
dict_TipoMovInv = {
    'idTipoMovInv': [1, 2, 3, 4, 5, 6],
    'codigo': ['ENTRADA', 'SALIDA', 'TRANSFERENCIA', 'AJUSTE', 'DEVOLUCION', 'MERMA'],
    'descripcion': [
        'Entrada de productos al inventario',
        'Salida de productos del inventario',
        'Transferencia entre almacenes',
        'Ajuste de inventario (positivo o negativo)',
        'Devolución de productos',
        'Pérdida o merma de productos'
    ]
}
df_tipoMovInv = pd.DataFrame(dict_TipoMovInv)

#! LOTE - Generar lotes por cada compra
lotes = []
id_lote_counter = 1
compra_totales = {}

for id_compra in range(1, cant_compra+1):
    # Cada compra tiene entre 1 y 8 productos diferentes
    num_productos = random.randint(1, 8)
    productos_comprados = random.sample(list(df_Producto['idProducto']), num_productos)
    
    total_compra = 0
    
    for id_producto in productos_comprados:
        producto_info = df_Producto[df_Producto['idProducto'] == id_producto].iloc[0]
        cantidad = random.randint(5, 50)
        costo_unitario = round(producto_info['costoRef'] * random.uniform(0.9, 1.1), 2)
        
        lotes.append({
            'idLote': id_lote_counter,
            'idCompra': id_compra,
            'idProducto': id_producto,
            'cantidad': cantidad,
            'costoUnitario': costo_unitario
        })
        
        total_compra += cantidad * costo_unitario
        id_lote_counter += 1
    
    compra_totales[id_compra] = round(total_compra, 2)

dict_lote = {
    'idLote': [l['idLote'] for l in lotes],
    'idCompra': [l['idCompra'] for l in lotes],
    'idProducto': [l['idProducto'] for l in lotes],
    'cantidad': [l['cantidad'] for l in lotes],
    'costoUnitario': [l['costoUnitario'] for l in lotes],
}
df_lote = pd.DataFrame(dict_lote)

# Actualizar totales de compra
dict_compra['total'] = [compra_totales.get(i, 0.0) for i in range(1, cant_compra+1)]
df_compra = pd.DataFrame(dict_compra)

#! LOTE ALMACEN - Distribuir lotes en almacenes
lotes_almacen = []
id_lote_almacen = 1

for _, lote in df_lote.iterrows():
    id_compra = lote['idCompra']
    sucursal_compra = df_compra[df_compra['idCompra'] == id_compra].iloc[0]['idSucursal']
    almacen_destino = df_Almacen[df_Almacen['idSucursal'] == sucursal_compra].iloc[0]['idAlmacen']
    
    cantidad_restante = lote['cantidad']
    
    # 80% va al almacén de la sucursal de compra
    cantidad_principal = int(cantidad_restante * 0.8)
    if cantidad_principal > 0:
        lotes_almacen.append({
            'idLoteAlmacen': id_lote_almacen,
            'idAlmacen': almacen_destino,
            'idLote': lote['idLote'],
            'cantidad': cantidad_principal
        })
        id_lote_almacen += 1
        cantidad_restante -= cantidad_principal
    
    # 20% restante puede distribuirse a otros almacenes
    if cantidad_restante > 0:
        otros_almacenes = df_Almacen[df_Almacen['idAlmacen'] != almacen_destino]['idAlmacen'].tolist()
        if otros_almacenes:
            almacen_secundario = random.choice(otros_almacenes)
            lotes_almacen.append({
                'idLoteAlmacen': id_lote_almacen,
                'idAlmacen': almacen_secundario,
                'idLote': lote['idLote'],
                'cantidad': cantidad_restante
            })
            id_lote_almacen += 1

dict_loteAlmacen = {
    'idLoteAlmacen': [la['idLoteAlmacen'] for la in lotes_almacen],
    'idAlmacen': [la['idAlmacen'] for la in lotes_almacen],
    'idLote': [la['idLote'] for la in lotes_almacen],
    'cantidad': [la['cantidad'] for la in lotes_almacen],
}
df_loteAlmacen = pd.DataFrame(dict_loteAlmacen)

#! STOCK - Calcular stock por producto y almacén
stock_dict = defaultdict(lambda: defaultdict(int))

for _, la in df_loteAlmacen.iterrows():
    lote_info = df_lote[df_lote['idLote'] == la['idLote']].iloc[0]
    id_producto = lote_info['idProducto']
    id_almacen = la['idAlmacen']
    cantidad = la['cantidad']
    
    stock_dict[id_almacen][id_producto] += cantidad

stocks = []
id_stock = 1

for id_almacen, productos in stock_dict.items():
    for id_producto, cantidad in productos.items():
        stocks.append({
            'idStock': id_stock,
            'idProducto': id_producto,
            'idAlmacen': id_almacen,
            'stock': cantidad,
            'stockMinimo': random.randint(3, 10)
        })
        id_stock += 1

dict_stock = {
    'idStock': [s['idStock'] for s in stocks],
    'idProducto': [s['idProducto'] for s in stocks],
    'idAlmacen': [s['idAlmacen'] for s in stocks],
    'stock': [s['stock'] for s in stocks],
    'stockMinimo': [s['stockMinimo'] for s in stocks],
}
df_stock = pd.DataFrame(dict_stock)

#! MOVIMIENTO INVENTARIO
movimientos = []
id_mov = 1
cant_movimientos = 150

for _ in range(cant_movimientos):
    fecha_mov = fk.date_between(fecha_inicio, fecha_fin)
    while fecha_mov.weekday() >= 5:
        fecha_mov = fk.date_between(fecha_inicio, fecha_fin)
    
    tipo_mov = random.choice([1, 3, 4])  # ENTRADA, TRANSFERENCIA, AJUSTE
    empleado = df_empleado.sample(1).iloc[0]['idEmpleado']
    almacen_destino = random.randint(1, 3)
    
    movimientos.append({
        'idMovInv': id_mov,
        'idTipoMovInv': tipo_mov,
        'idEmpleado': empleado,
        'idAlmacenDestino': almacen_destino,
        'fecha': fecha_mov
    })
    id_mov += 1

dict_movInv = {
    'idMovInv': [m['idMovInv'] for m in movimientos],
    'idTipoMovInv': [m['idTipoMovInv'] for m in movimientos],
    'idEmpleado': [m['idEmpleado'] for m in movimientos],
    'idAlmacenDestino': [m['idAlmacenDestino'] for m in movimientos],
    'fecha': [m['fecha'] for m in movimientos],
}
df_movInv = pd.DataFrame(dict_movInv)

#! MOVIMIENTO INVENTARIO DETALLE
mov_detalles = []
id_detalle = 1

for _, mov in df_movInv.iterrows():
    num_items = random.randint(1, 5)
    lotes_disponibles = df_loteAlmacen.sample(min(num_items, len(df_loteAlmacen)))
    
    for _, lote_alm in lotes_disponibles.iterrows():
        cantidad_dev = random.randint(1, min(5, round(lote_alm['cantidad'])))
        mov_detalles.append({
            'idMovInvDetalle': id_detalle,
            'idMovInv': mov['idMovInv'],
            'idLoteAlmacen': lote_alm['idLoteAlmacen'],
            'cantidad': cantidad
        })
        id_detalle += 1

dict_movInvDetalle = {
    'idMovInvDetalle': [md['idMovInvDetalle'] for md in mov_detalles],
    'idMovInv': [md['idMovInv'] for md in mov_detalles],
    'idLoteAlmacen': [md['idLoteAlmacen'] for md in mov_detalles],
    'cantidad': [md['cantidad'] for md in mov_detalles],
}
df_movInvDetalle = pd.DataFrame(dict_movInvDetalle)

#! CAJA
cajas = []
id_caja = 1

for sucursal in range(1, cant_sucursales+1):
    num_cajas = random.randint(2, 4)
    for i in range(num_cajas):
        cajas.append({
            'idCaja': id_caja,
            'idSucursal': sucursal,
            'codigo': f"CAJA-{sucursal:02d}-{i+1:02d}",
            'activa': 'ACTIVA' if random.random() > 0.1 else 'INACTIVA'
        })
        id_caja += 1

dict_caja = {
    'idCaja': [c['idCaja'] for c in cajas],
    'idSucursal': [c['idSucursal'] for c in cajas],
    'codigo': [c['codigo'] for c in cajas],
    'activa': [c['activa'] for c in cajas],
}
df_caja = pd.DataFrame(dict_caja)

#! SESION CAJA
sesiones = []
id_sesion = 1
cant_sesiones = 400

for _ in range(cant_sesiones):
    fecha_sesion = fk.date_between(fecha_inicio, fecha_fin)
    while fecha_sesion.weekday() >= 5:
        fecha_sesion = fk.date_between(fecha_inicio, fecha_fin)
    
    caja = df_caja[df_caja['activa'] == 'ACTIVA'].sample(1).iloc[0]
    empleado = df_empleado[df_empleado['activo'] == 'ACTIVO'].sample(1).iloc[0]['idEmpleado']
    
    monto_apertura = round(random.uniform(500, 2000), 2)
    monto_cierre = round(monto_apertura + random.uniform(-50, 5000), 2)
    diferencia = round(monto_cierre - monto_apertura, 2)
    
    sesiones.append({
        'idSesionCaja': id_sesion,
        'idCaja': caja['idCaja'],
        'idEmpleado': empleado,
        'fecha': fecha_sesion,
        'montoApertura': monto_apertura,
        'montoCierre': monto_cierre,
        'diferencia': diferencia,
        'estado': 'CERRADA' if random.random() > 0.1 else 'ABIERTA'
    })
    id_sesion += 1

dict_sesionCaja = {
    'idSesionCaja': [s['idSesionCaja'] for s in sesiones],
    'idCaja': [s['idCaja'] for s in sesiones],
    'idEmpleado': [s['idEmpleado'] for s in sesiones],
    'fecha': [s['fecha'] for s in sesiones],
    'montoApertura': [s['montoApertura'] for s in sesiones],
    'montoCierre': [s['montoCierre'] for s in sesiones],
    'diferencia': [s['diferencia'] for s in sesiones],
    'estado': [s['estado'] for s in sesiones],
}
df_sesionCaja = pd.DataFrame(dict_sesionCaja)

#! TRABAJO
trabajos_servicios = [
    ('Cambio de pantalla', 'Reemplazo completo de pantalla LCD/OLED', 150),
    ('Cambio de batería', 'Reemplazo de batería original', 80),
    ('Reparación de puerto de carga', 'Limpieza y/o cambio de puerto', 60),
    ('Instalación de memoria RAM', 'Instalación y configuración de RAM', 40),
    ('Instalación de disco duro/SSD', 'Instalación y configuración de almacenamiento', 50),
    ('Formateo e instalación de SO', 'Formateo completo e instalación de sistema operativo', 100),
    ('Limpieza profunda', 'Limpieza interna completa del equipo', 70),
    ('Cambio de teclado', 'Reemplazo de teclado completo', 90),
    ('Reparación de bisagra', 'Reparación o cambio de bisagra', 85),
    ('Diagnóstico técnico', 'Diagnóstico completo del equipo', 30),
    ('Cambio de cámara', 'Reemplazo de cámara frontal o trasera', 110),
    ('Reparación de touchpad', 'Reparación o cambio de touchpad', 65),
    ('Cambio de ventilador', 'Reemplazo de sistema de ventilación', 75),
    ('Actualización de software', 'Actualización y optimización de software', 45),
    ('Recuperación de datos', 'Recuperación de información de discos', 200),
]

dict_trabajo = {
    'idTrabajo': range(1, len(trabajos_servicios)+1),
    'nombre': [t[0] for t in trabajos_servicios],
    'descripcionServicio': [t[1] for t in trabajos_servicios],
    'precioReferencia': [t[2] for t in trabajos_servicios],
}
df_trabajo = pd.DataFrame(dict_trabajo)

#! METODO PAGO
dict_metodoPago = {
    'idMetodoPago': [1, 2, 3, 4, 5],
    'nombre': ['Efectivo', 'Tarjeta de crédito', 'Tarjeta de débito', 'Transferencia bancaria', 'QR'],
}
df_metodoPago = pd.DataFrame(dict_metodoPago)

#! CLIENTE
cant_clientes = 500
dict_cliente = {
    'idCliente': range(1, cant_clientes+1),
    'nombre': [fk.first_name() for _ in range(cant_clientes)],
    'apellidoP': [fk.last_name() for _ in range(cant_clientes)],
    'apellidoM': [fk.last_name() for _ in range(cant_clientes)],
    'telefono': [str(random.randint(60000000, 79999999)) for _ in range(cant_clientes)],
    'direccion': [fk.address().replace('\n', ', ') for _ in range(cant_clientes)],
    'email': [fk.email() for _ in range(cant_clientes)],
}
df_cliente = pd.DataFrame(dict_cliente)

#! VENTA
ventas = []
id_venta = 1
cant_ventas = 1200

for _ in range(cant_ventas):
    fecha_venta = fk.date_between(fecha_inicio, fecha_fin)
    while fecha_venta.weekday() >= 5:
        fecha_venta = fk.date_between(fecha_inicio, fecha_fin)
    
    cliente = df_cliente.sample(1).iloc[0]['idCliente']
    empleado = df_empleado[df_empleado['activo'] == 'ACTIVO'].sample(1).iloc[0]['idEmpleado']
    sesion = df_sesionCaja[df_sesionCaja['fecha'] <= fecha_venta].sample(1).iloc[0]['idSesionCaja'] if len(df_sesionCaja[df_sesionCaja['fecha'] <= fecha_venta]) > 0 else df_sesionCaja.sample(1).iloc[0]['idSesionCaja']
    metodo_pago = random.randint(1, 5)
    
    ventas.append({
        'idVenta': id_venta,
        'idCliente': cliente,
        'idEmpleado': empleado,
        'idSesionCaja': sesion,
        'idMetodoPago': metodo_pago,
        'fecha': fecha_venta,
        'subTotal': 0.0,  # Se calculará después
        'total': 0.0,  # Se calculará después
        'estado': 'COMPLETADA' if random.random() > 0.05 else 'CANCELADA'
    })
    id_venta += 1

#! VENTA DETALLE
venta_detalles = []
id_venta_detalle = 1
venta_totales = {}

for venta in ventas:
    if venta['estado'] == 'CANCELADA':
        venta_totales[venta['idVenta']] = {'subTotal': 0.0, 'total': 0.0}
        continue
    
    num_items = random.randint(1, 6)
    lotes_venta = df_loteAlmacen.sample(min(num_items, len(df_loteAlmacen)))
    
    subtotal = 0
    
    for _, lote_alm in lotes_venta.iterrows():
        lote_info = df_lote[df_lote['idLote'] == lote_alm['idLote']].iloc[0]
        producto_info = df_Producto[df_Producto['idProducto'] == lote_info['idProducto']].iloc[0]
        
        cantidad = random.randint(1, 3)
        precio_unitario = round(producto_info['precioVenta'], 2)
        
        venta_detalles.append({
            'idVentaDetalle': id_venta_detalle,
            'idVenta': venta['idVenta'],
            'idLoteAlmacen': lote_alm['idLoteAlmacen'],
            'cantidad': cantidad,
            'precioUnitario': precio_unitario
        })
        
        subtotal += cantidad * precio_unitario
        id_venta_detalle += 1
    
    total = round(subtotal, 2)
    venta_totales[venta['idVenta']] = {'subTotal': total, 'total': total}

dict_ventaDetalle = {
    'idVentaDetalle': [vd['idVentaDetalle'] for vd in venta_detalles],
    'idVenta': [vd['idVenta'] for vd in venta_detalles],
    'idLoteAlmacen': [vd['idLoteAlmacen'] for vd in venta_detalles],
    'cantidad': [vd['cantidad'] for vd in venta_detalles],
    'precioUnitario': [vd['precioUnitario'] for vd in venta_detalles],
}
df_ventaDetalle = pd.DataFrame(dict_ventaDetalle)

# Actualizar totales de venta
for venta in ventas:
    totales = venta_totales.get(venta['idVenta'], {'subTotal': 0.0, 'total': 0.0})
    venta['subTotal'] = totales['subTotal']
    venta['total'] = totales['total']

dict_venta = {
    'idVenta': [v['idVenta'] for v in ventas],
    'idCliente': [v['idCliente'] for v in ventas],
    'idEmpleado': [v['idEmpleado'] for v in ventas],
    'idSesionCaja': [v['idSesionCaja'] for v in ventas],
    'idMetodoPago': [v['idMetodoPago'] for v in ventas],
    'fecha': [v['fecha'] for v in ventas],
    'subTotal': [v['subTotal'] for v in ventas],
    'total': [v['total'] for v in ventas],
    'estado': [v['estado'] for v in ventas],
}
df_venta = pd.DataFrame(dict_venta)

#! DEVOLUCION
devoluciones = []
id_devolucion = 1
cant_devoluciones = 50

detalles_disponibles = df_ventaDetalle[df_ventaDetalle['idVenta'].isin(
    df_venta[df_venta['estado'] == 'COMPLETADA']['idVenta']
)]

for _ in range(min(cant_devoluciones, len(detalles_disponibles))):
    detalle = detalles_disponibles.sample(1).iloc[0]
    venta_info = df_venta[df_venta['idVenta'] == detalle['idVenta']].iloc[0]
    
    fecha_devolucion = venta_info['fecha'] + timedelta(days=random.randint(1, 30))
    cantidad_dev = random.randint(1, round(detalle['cantidad']))

    
    devoluciones.append({
        'idDevolucion': id_devolucion,
        'idVentaDetalle': detalle['idVentaDetalle'],
        'fecha': fecha_devolucion,
        'cantidad': cantidad_dev
    })
    id_devolucion += 1

dict_devolucion = {
    'idDevolucion': [d['idDevolucion'] for d in devoluciones],
    'idVentaDetalle': [d['idVentaDetalle'] for d in devoluciones],
    'fecha': [d['fecha'] for d in devoluciones],
    'cantidad': [d['cantidad'] for d in devoluciones],
}
df_devolucion = pd.DataFrame(dict_devolucion)

#! EQUIPO CLIENTE
equipos = []
id_equipo = 1
tipos_equipo = ['Smartphone', 'Laptop', 'Tablet', 'Desktop', 'Smartwatch']

for cliente_id in df_cliente['idCliente'].sample(300):
    num_equipos = random.randint(1, 3)
    for _ in range(num_equipos):
        marca = random.choice(['Samsung', 'Apple', 'HP', 'Dell', 'Lenovo', 'Asus', 'Xiaomi'])
        tipo = random.choice(tipos_equipo)
        
        equipos.append({
            'idEquipoCliente': id_equipo,
            'marca': marca,
            'modelo': f"{marca} {fk.word().capitalize()} {random.randint(100, 999)}",
            'idCliente': cliente_id,
            'tipoEquipo': tipo,
            'nroSerie': fk.bothify(text='??########').upper()
        })
        id_equipo += 1

dict_equipoCliente = {
    'idEquipoCliente': [e['idEquipoCliente'] for e in equipos],
    'marca': [e['marca'] for e in equipos],
    'modelo': [e['modelo'] for e in equipos],
    'idCliente': [e['idCliente'] for e in equipos],
    'tipoEquipo': [e['tipoEquipo'] for e in equipos],
    'nroSerie': [e['nroSerie'] for e in equipos],
}
df_equipoCliente = pd.DataFrame(dict_equipoCliente)

#! ORDEN SERVICIO
ordenes = []
id_orden = 1
cant_ordenes = 400

for _ in range(cant_ordenes):
    equipo = df_equipoCliente.sample(1).iloc[0]
    empleado = df_empleado[df_empleado['cargo'] == 'Tecnico'].sample(1).iloc[0]['idEmpleado'] if len(df_empleado[df_empleado['cargo'] == 'Tecnico']) > 0 else df_empleado.sample(1).iloc[0]['idEmpleado']
    
    fecha_ingreso = fk.date_between(fecha_inicio, fecha_fin)
    while fecha_ingreso.weekday() >= 5:
        fecha_ingreso = fk.date_between(fecha_inicio, fecha_fin)
    
    dias_reparacion = random.randint(1, 15)
    fecha_entrega = fecha_ingreso + timedelta(days=dias_reparacion)
    
    # Algunas órdenes tienen venta asociada
    venta_id = None
    if random.random() > 0.3:
        ventas_disponibles = df_venta[
            (df_venta['fecha'] >= fecha_ingreso) & 
            (df_venta['estado'] == 'COMPLETADA')
        ]
        if len(ventas_disponibles) > 0:
            venta_id = ventas_disponibles.sample(1).iloc[0]['idVenta']
    
    estados = ['COMPLETADA', 'EN PROCESO', 'PENDIENTE', 'ENTREGADA']
    estado = random.choices(estados, weights=[50, 20, 10, 20])[0]
    
    costo = round(random.uniform(100, 800), 2)
    
    ordenes.append({
        'idOrdenServicio': id_orden,
        'idEquipoCliente': equipo['idEquipoCliente'],
        'idEmpleado': empleado,
        'idVenta': venta_id if venta_id else ordenes[0]['idVenta'] if len(ordenes) > 0 else 1,  # Evitar NULL
        'fechaIngreso': fecha_ingreso,
        'fechaEntrega': fecha_entrega,
        'estado': estado,
        'costo': costo
    })
    id_orden += 1

dict_ordenServicio = {
    'idOrdenServicio': [o['idOrdenServicio'] for o in ordenes],
    'idEquipoCliente': [o['idEquipoCliente'] for o in ordenes],
    'idEmpleado': [o['idEmpleado'] for o in ordenes],
    'idVenta': [o['idVenta'] for o in ordenes],
    'fechaIngreso': [o['fechaIngreso'] for o in ordenes],
    'fechaEntrega': [o['fechaEntrega'] for o in ordenes],
    'estado': [o['estado'] for o in ordenes],
    'costo': [o['costo'] for o in ordenes],
}
df_ordenServicio = pd.DataFrame(dict_ordenServicio)

#! PEDIDO MATERIAL
pedidos_material = []
id_pedido = 1
cant_pedidos = 80

for _ in range(cant_pedidos):
    orden = df_ordenServicio.sample(1).iloc[0]
    compra = df_compra.sample(1).iloc[0]
    
    fecha_pedido = orden['fechaIngreso'] + timedelta(days=random.randint(0, 3))
    estados_pedido = ['RECIBIDO', 'PENDIENTE', 'EN TRANSITO']
    
    pedidos_material.append({
        'idPedidoMaterial': id_pedido,
        'idCompra': compra['idCompra'],
        'idOrdenServicio': orden['idOrdenServicio'],
        'descripcionMaterial': f"Material para reparación - {fk.sentence(nb_words=4)}",
        'fechaPedido': fecha_pedido,
        'estadoPedido': random.choice(estados_pedido)
    })
    id_pedido += 1

dict_pedidoMaterial = {
    'idPedidoMaterial': [pm['idPedidoMaterial'] for pm in pedidos_material],
    'idCompra': [pm['idCompra'] for pm in pedidos_material],
    'idOrdenServicio': [pm['idOrdenServicio'] for pm in pedidos_material],
    'descripcionMaterial': [pm['descripcionMaterial'] for pm in pedidos_material],
    'fechaPedido': [pm['fechaPedido'] for pm in pedidos_material],
    'estadoPedido': [pm['estadoPedido'] for pm in pedidos_material],
}
df_pedidoMaterial = pd.DataFrame(dict_pedidoMaterial)

#! DETALLE ORDEN SERVICIO
detalles_orden = []
id_detalle_orden = 1

for orden_id in df_ordenServicio['idOrdenServicio']:
    num_trabajos = random.randint(1, 4)
    trabajos_orden = df_trabajo.sample(min(num_trabajos, len(df_trabajo)))
    
    for _, trabajo in trabajos_orden.iterrows():
        precio_cobrado = round(trabajo['precioReferencia'] * random.uniform(0.9, 1.3), 2)
        
        detalles_orden.append({
            'idDetalleOrdenServicio': id_detalle_orden,
            'idOrdenServicio': orden_id,
            'idTrabajo': trabajo['idTrabajo'],
            'precioCobrado': precio_cobrado,
            'notaTecnica': fk.sentence(nb_words=8)
        })
        id_detalle_orden += 1

dict_detalleOrdenServicio = {
    'idDetalleOrdenServicio': [do['idDetalleOrdenServicio'] for do in detalles_orden],
    'idOrdenServicio': [do['idOrdenServicio'] for do in detalles_orden],
    'idTrabajo': [do['idTrabajo'] for do in detalles_orden],
    'precioCobrado': [do['precioCobrado'] for do in detalles_orden],
    'notaTecnica': [do['notaTecnica'] for do in detalles_orden],
}
df_detalleOrdenServicio = pd.DataFrame(dict_detalleOrdenServicio)

#! REPARACION MATERIAL
reparaciones_mat = []
id_rep_mat = 1

for orden_id in df_ordenServicio['idOrdenServicio'].sample(250):
    num_materiales = random.randint(1, 5)
    lotes_rep = df_loteAlmacen.sample(min(num_materiales, len(df_loteAlmacen)))
    
    for _, lote_alm in lotes_rep.iterrows():
        lote_info = df_lote[df_lote['idLote'] == lote_alm['idLote']].iloc[0]
        
        cantidad = random.randint(1, 3)
        precio_unitario = round(lote_info['costoUnitario'] * 1.4, 2)
        
        reparaciones_mat.append({
            'idReparacionMat': id_rep_mat,
            'idOrdenServicio': orden_id,
            'idLoteAlmacen': lote_alm['idLoteAlmacen'],
            'cantida': cantidad,  # Nota: typo en el esquema original
            'precioUnitario': precio_unitario
        })
        id_rep_mat += 1

dict_reparacionMat = {
    'idReparacionMat': [rm['idReparacionMat'] for rm in reparaciones_mat],
    'idOrdenServicio': [rm['idOrdenServicio'] for rm in reparaciones_mat],
    'idLoteAlmacen': [rm['idLoteAlmacen'] for rm in reparaciones_mat],
    'cantida': [rm['cantida'] for rm in reparaciones_mat],
    'precioUnitario': [rm['precioUnitario'] for rm in reparaciones_mat],
}
df_reparacionMat = pd.DataFrame(dict_reparacionMat)

#! EXPORTAR A CSV
print("Exportando DataFrames a CSV...")

df_sucursal.to_csv('sucursal.csv', index=False, encoding='utf-8-sig')
df_Almacen.to_csv('almacen.csv', index=False, encoding='utf-8-sig')
df_MarcaProducto.to_csv('marcaProducto.csv', index=False, encoding='utf-8-sig')
df_ModeloProducto.to_csv('modeloProducto.csv', index=False, encoding='utf-8-sig')
df_Producto.to_csv('producto.csv', index=False, encoding='utf-8-sig')
df_Proveedor.to_csv('proveedor.csv', index=False, encoding='utf-8-sig')
df_empleado.to_csv('empleado.csv', index=False, encoding='utf-8-sig')
df_Gasto.to_csv('gasto.csv', index=False, encoding='utf-8-sig')
df_compra.to_csv('compra.csv', index=False, encoding='utf-8-sig')
df_tipoMovInv.to_csv('tipoMovInv.csv', index=False, encoding='utf-8-sig')
df_movInv.to_csv('movInv.csv', index=False, encoding='utf-8-sig')
df_stock.to_csv('stock.csv', index=False, encoding='utf-8-sig')
df_lote.to_csv('lote.csv', index=False, encoding='utf-8-sig')
df_loteAlmacen.to_csv('loteAlmacen.csv', index=False, encoding='utf-8-sig')
df_movInvDetalle.to_csv('movInvDetalle.csv', index=False, encoding='utf-8-sig')
df_caja.to_csv('caja.csv', index=False, encoding='utf-8-sig')
df_sesionCaja.to_csv('sesionCaja.csv', index=False, encoding='utf-8-sig')
df_trabajo.to_csv('trabajo.csv', index=False, encoding='utf-8-sig')
df_metodoPago.to_csv('metodoPago.csv', index=False, encoding='utf-8-sig')
df_cliente.to_csv('cliente.csv', index=False, encoding='utf-8-sig')
df_venta.to_csv('venta.csv', index=False, encoding='utf-8-sig')
df_ventaDetalle.to_csv('ventaDetalle.csv', index=False, encoding='utf-8-sig')
df_devolucion.to_csv('devolucion.csv', index=False, encoding='utf-8-sig')
df_equipoCliente.to_csv('equipoCliente.csv', index=False, encoding='utf-8-sig')
df_ordenServicio.to_csv('ordenServicio.csv', index=False, encoding='utf-8-sig')
df_pedidoMaterial.to_csv('pedidoMaterial.csv', index=False, encoding='utf-8-sig')
df_detalleOrdenServicio.to_csv('detalleOrdenServicio.csv', index=False, encoding='utf-8-sig')
df_reparacionMat.to_csv('reparacionMat.csv', index=False, encoding='utf-8-sig')

print("\n✅ Exportación completada!")
print(f"\nResumen de registros generados:")
print(f"- Sucursales: {len(df_sucursal)}")
print(f"- Almacenes: {len(df_Almacen)}")
print(f"- Marcas: {len(df_MarcaProducto)}")
print(f"- Modelos: {len(df_ModeloProducto)}")
print(f"- Productos: {len(df_Producto)}")
print(f"- Proveedores: {len(df_Proveedor)}")
print(f"- Empleados: {len(df_empleado)}")
print(f"- Gastos: {len(df_Gasto)}")
print(f"- Compras: {len(df_compra)}")
print(f"- Lotes: {len(df_lote)}")
print(f"- Lotes en Almacén: {len(df_loteAlmacen)}")
print(f"- Stock: {len(df_stock)}")
print(f"- Movimientos Inv: {len(df_movInv)}")
print(f"- Detalles Mov Inv: {len(df_movInvDetalle)}")
print(f"- Cajas: {len(df_caja)}")
print(f"- Sesiones Caja: {len(df_sesionCaja)}")
print(f"- Trabajos: {len(df_trabajo)}")
print(f"- Métodos Pago: {len(df_metodoPago)}")
print(f"- Clientes: {len(df_cliente)}")
print(f"- Ventas: {len(df_venta)}")
print(f"- Detalles Venta: {len(df_ventaDetalle)}")
print(f"- Devoluciones: {len(df_devolucion)}")
print(f"- Equipos Cliente: {len(df_equipoCliente)}")
print(f"- Órdenes Servicio: {len(df_ordenServicio)}")
print(f"- Pedidos Material: {len(df_pedidoMaterial)}")
print(f"- Detalles Orden: {len(df_detalleOrdenServicio)}")
print(f"- Reparación Material: {len(df_reparacionMat)}")




# Conexión con pyodbc
conn = pyodbc.connect(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"Trusted_Connection=yes;"
)

# Engine para SQLAlchemy
engine = create_engine(
    f"mssql+pyodbc://localhost/{database}"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&trusted_connection=yes"
)

print("✅ Conexión establecida exitosamente\n")

# Función para insertar datos
def insertar_tabla(df, nombre_tabla, cursor, conn):
    """
    Inserta un DataFrame en SQL Server
    """
    print(f"📝 Insertando {len(df)} registros en tabla '{nombre_tabla}'...")
    
    try:
        # Preparar los datos
        columnas = ', '.join(df.columns)
        placeholders = ', '.join(['?' for _ in df.columns])
        sql = f"INSERT INTO {nombre_tabla} ({columnas}) VALUES ({placeholders})"
        
        # Convertir DataFrame a lista de tuplas
        datos = [tuple(row) for row in df.values]
        
        # Ejecutar inserción
        cursor.executemany(sql, datos)
        conn.commit()
        
        print(f"   ✅ {len(df)} registros insertados correctamente\n")
        return True
        
    except Exception as e:
        print(f"   ❌ Error en tabla '{nombre_tabla}': {str(e)}\n")
        conn.rollback()
        return False

# Crear cursor
cursor = conn.cursor()

print("="*70)
print("INICIANDO CARGA DE DATOS A SQL SERVER")
print("="*70)
print()

# ORDEN DE INSERCIÓN (respetando dependencias de FK)
orden_insercion = [
    # 1. Tablas sin dependencias
    ('sucursal', df_sucursal),
    ('marcaProducto', df_MarcaProducto),
    ('proveedor', df_Proveedor),
    ('empleado', df_empleado),
    ('tipoMovInv', df_tipoMovInv),
    ('trabajo', df_trabajo),
    ('metodoPago', df_metodoPago),
    ('cliente', df_cliente),
    
    # 2. Tablas con 1 nivel de dependencia
    ('almacen', df_Almacen),  # depende de sucursal
    ('modeloProducto', df_ModeloProducto),  # depende de marcaProducto
    ('gasto', df_Gasto),  # depende de sucursal, empleado
    ('caja', df_caja),  # depende de sucursal
    ('equipoCliente', df_equipoCliente),  # depende de cliente
    
    # 3. Tablas con 2 niveles de dependencia
    ('producto', df_Producto),  # depende de marcaProducto, modeloProducto
    ('compra', df_compra),  # depende de proveedor, empleado, sucursal
    ('stock', df_stock),  # depende de producto, almacen
    ('sesionCaja', df_sesionCaja),  # depende de caja, empleado
    ('movInv', df_movInv),  # depende de tipoMovInv, empleado, almacen
    
    # 4. Tablas con 3 niveles de dependencia
    ('lote', df_lote),  # depende de compra, producto
    ('venta', df_venta),  # depende de cliente, empleado, sesionCaja, metodoPago
    
    # 5. Tablas con 4 niveles de dependencia
    ('loteAlmacen', df_loteAlmacen),  # depende de almacen, lote
    
    # 6. Tablas con 5 niveles de dependencia
    ('movInvDetalle', df_movInvDetalle),  # depende de movInv, loteAlmacen
    ('ventaDetalle', df_ventaDetalle),  # depende de venta, loteAlmacen
    ('ordenServicio', df_ordenServicio),  # depende de equipoCliente, empleado, venta
    
    # 7. Tablas con 6 niveles de dependencia
    ('devolucion', df_devolucion),  # depende de ventaDetalle
    ('pedidoMaterial', df_pedidoMaterial),  # depende de compra, ordenServicio
    ('detalleOrdenServicio', df_detalleOrdenServicio),  # depende de ordenServicio, trabajo
    ('reparacionMat', df_reparacionMat),  # depende de ordenServicio, loteAlmacen
]

# Contador de éxitos y errores
exitos = 0
errores = 0
tablas_con_error = []

# Ejecutar inserción en orden
for nombre_tabla, dataframe in orden_insercion:
    if insertar_tabla(dataframe, nombre_tabla, cursor, conn):
        exitos += 1
    else:
        errores += 1
        tablas_con_error.append(nombre_tabla)

# Cerrar cursor y conexión
cursor.close()
conn.close()

# Resumen final
print("="*70)
print("RESUMEN DE CARGA DE DATOS")
print("="*70)
print(f"✅ Tablas insertadas correctamente: {exitos}")
print(f"❌ Tablas con errores: {errores}")

if tablas_con_error:
    print(f"\n⚠️  Tablas que fallaron:")
    for tabla in tablas_con_error:
        print(f"   - {tabla}")
else:
    print("\n🎉 ¡TODOS LOS DATOS SE INSERTARON EXITOSAMENTE!")

print("="*70)