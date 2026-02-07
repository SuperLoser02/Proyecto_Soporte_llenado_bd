--use COLEGIO
--drop database PROYECTO
create database PROYECTO;
use PROYECTO;

create table sucursal(
    idSucursal INT PRIMARY KEY,
    nombre NVARCHAR(100) NOT NULL,
    direccion NVARCHAR(200) NOT NULL,
    telefono NVARCHAR(20),
    ubicacion NVARCHAR(150),
    activa BIT
);

create table almacen(
	idAlmacen int primary key,
	idSucursal int not null,
	descripcion nvarchar(200),
	CONSTRAINT fk_almacen FOREIGN KEY (idSucursal) 
        REFERENCES Sucursal(idSucursal),
);

create table marcaProducto(
	idMarca int primary key,
	nombre nvarchar(100),
	descripcion nvarchar(200)
);

create table modeloProducto(
	idModelo int primary key,
	idMarca int,
	nombre nvarchar(100),
	descripcion nvarchar(200),
	constraint fk_modelo_producto foreign key (idMarca)
	references marcaProducto(idMarca)
);

create table producto(
	idProducto int primary key,
	idMarca int,
	idModelo int,
	codigo nvarchar(100),
	nombre nvarchar(100),
	descripcion nvarchar(200),
	precioVenta DECIMAL(10,2) NOT NULL,
	costoRef DECIMAL(10,2) NOT NULL,
	tipoPrecio nvarchar(200),
	constraint fk_producto_ma foreign key (idMarca)
	references marcaProducto(idMarca),
	constraint fk_producto_mo foreign key (idModelo)
	references modeloProducto(idModelo)
);

create table proveedor(
	idProveedor int primary key,
	razonSocial nvarchar(100),
	nit nvarchar(100),
	telefono nvarchar(100),
	direccion nvarchar(100),
	email nvarchar(100),
	activo nvarchar(100),
);

create table empleado(
	idEmpleado int primary key,
	nombre nvarchar(100),
	apellidoP nvarchar(100),
	apellidoM nvarchar(100),
	telefono nvarchar(100),
	cargo nvarchar(100),
	direccion nvarchar(200),
	email nvarchar(100),
	activo nvarchar(100)
);


create table gasto(
	idGasto int primary key,
	idSucursal int,
	idEmpleado int,
	fecha date,
	concepto nvarchar(100),
	monto DECIMAL(10,2) NOT NULL,
	comprobante nvarchar(100),
	constraint fk_gasto_sucursal foreign key (idSucursal)
	references sucursal(idSucursal),
	constraint fk_gasto_empleado foreign key (idEmpleado)
	references empleado(idEmpleado)
);

create table compra(
	idCompra int primary key,
	idProveedor int,
	idEmpleado int,
	idSucursal int,
	fecha date,
	total DECIMAL(10,2) NOT NULL,
	estado nvarchar(100),
	constraint fk_compra_proveedor foreign key(idProveedor)
	references proveedor(idProveedor),
	constraint fk_compra_empleado foreign key(idEmpleado)
	references empleado(idEmpleado),
	constraint fk_compra_idSucursal foreign key(idSucursal)
	references sucursal(idSucursal)
);

create table tipoMovInv(
	idTipoMovInv int primary key,
	codigo nvarchar(100),
	descripcion nvarchar(200)
);

create table movInv(
	idMovInv int primary key,
	idTipoMovInv int,
	idEmpleado int,
	idAlmacenDestino int,
	fecha date,
	constraint fk_movInv_Tipo foreign key(idTipoMovInv)
	references tipoMovInv(idTipoMovInv),
	constraint fk_movInv_Empleado foreign key(idEmpleado)
	references empleado(idEmpleado),
	constraint fk_movInv_Almacen foreign key(idAlmacenDestino)
	references almacen(idAlmacen)	
);

create table stock(
	idStock int primary key,
	idProducto int,
	idAlmacen int,
	stock int,
	stockMinimo int,
	constraint fk_stock_almacen foreign key (idAlmacen)
	references almacen(idAlmacen),
	constraint fk_stock_producto foreign key (idProducto)
	references producto(idProducto)
);

create table lote(
	idLote int primary key,
	idCompra int,
	idProducto int,
	cantidad int,
	costoUnitario DECIMAL(10,2) NOT NULL,
	constraint fk_lote_compra foreign key (idCompra)
	references compra(idCompra),
	constraint fk_lote_producto foreign key (idProducto)
	references producto(idProducto)
);

create table loteAlmacen(
	idLoteAlmacen int primary key,
	idAlmacen int,
	idLote int,
	cantidad int,
	constraint fk_loteAlmacen_almacen foreign key(idAlmacen)
	references almacen(idAlmacen),
	constraint fk_loteAlmacen_lote foreign key(idLote)
	references lote(idLote)
);

create table movInvDetalle(
	idMovInvDetalle int primary key,
	idMovInv int,
	idLoteAlmacen int,
	cantidad int,
	constraint fk_movInvDetalle_movInv foreign key(idMovInv)
	references movInv(idMovInv),
	constraint fk_movInvDetalle_lote foreign key(idLoteAlmacen)
	references loteAlmacen(idLoteAlmacen)
);

create table caja(
	idCaja int primary key,
	idSucursal int,
	codigo nvarchar(100),
	activa nvarchar(100),
	constraint fk_caja_sucursal foreign key(idSucursal)
	references sucursal(idSucursal)
);

create table sesionCaja(
	idSesionCaja int primary key,
	idCaja int,
	idEmpleado int,
	fecha date,
	montoApertura DECIMAL(10,2) NOT NULL,
	montoCierre DECIMAL(10,2) NOT NULL,
	diferencia DECIMAL(10,2) NOT NULL,
	estado nvarchar(100),
	constraint fk_sesionCaja_caja foreign key(idCaja)
	references caja(idCaja),
	constraint fk_sesionCaja_empleado foreign key(idEmpleado)
	references empleado(idEmpleado)
);

create table trabajo(
	idTrabajo int primary key,
	nombre nvarchar(100),
	descripcionServicio nvarchar(200),
	precioReferencia DECIMAL(10,2) NOT NULL
);

create table metodoPago(
	idMetodoPago int primary key,
	nombre nvarchar(100)
);

create table cliente(
	idCliente int primary key,
	nombre nvarchar(100),
	apellidoP nvarchar(100),
	apellidoM nvarchar(100),
	telefono nvarchar(100),
	direccion nvarchar(200),
	email nvarchar(100),
);

create table venta(
	idVenta int primary key,
	idCliente int,
	idEmpleado int,
	idSesionCaja int,
	idMetodoPago int,
	fecha date,
	subTotal DECIMAL(10,2) NOT NULL,
	total DECIMAL(10,2) NOT NULL,
	estado nvarchar(100),
	constraint fk_venta_cliente foreign key(idCliente)
	references cliente(idCliente),
	constraint fk_venta_empleado foreign key(idEmpleado)
	references empleado(idEmpleado),
	constraint fk_venta_sesion foreign key(idSesionCaja)
	references sesionCaja(idSesionCaja),
	constraint fk_venta_metodoPago foreign key(idMetodoPago)
	references metodoPago(idMetodoPago)
);

create table ventaDetalle(
	idVentaDetalle int primary key,
	idVenta int,
	idLoteAlmacen int,
	cantidad int,
	precioUnitario DECIMAL(10,2) NOT NULL,
	constraint fk_ventaDetalle_Venta foreign key(idVenta)
	references venta(idVenta),
	constraint fk_ventaDetalle foreign key(idLoteAlmacen)
	references loteAlmacen(idLoteAlmacen)
);

create table devolucion(
	idDevolucion int primary key,
	idVentaDetalle int,
	fecha date,
	cantidad int,
	constraint fk_devolucion foreign key(idVentaDetalle)
	references ventaDetalle(idVentaDetalle)
);

create table equipoCliente(
	idEquipoCliente int primary key,
	marca nvarchar(100),
	modelo nvarchar(100),
	idCliente int,
	tipoEquipo nvarchar(100),
	nroSerie nvarchar(100),
	constraint fk_equipoCliente foreign key (idCliente)
	references cliente(idCliente)
);

create table ordenServicio(
	idOrdenServicio int primary key,
	idEquipoCliente int,
	idEmpleado int,
	idVenta int,
	fechaIngreso date,
	fechaEntrega date,
	estado nvarchar(100),
	costo DECIMAL(10,2) NOT NULL,
	constraint fk_ordenServicio_equipoCliente foreign key (idEquipoCliente)
	references equipoCliente(idEquipoCliente),
	constraint fk_ordenServicio_empleado foreign key (idEmpleado)
	references empleado(idEmpleado),
	constraint fk_ordenServicio_venta foreign key (idVenta)
	references venta(idVenta)
);

create table pedidoMaterial(
	idPedidoMaterial int primary key,
	idCompra int,
	idOrdenServicio int,
	descripcionMaterial nvarchar(200),
	fechaPedido date,
	estadoPedido nvarchar(100),
	constraint fk_pedidoMaterial_ordenServicio foreign key (idOrdenServicio)
	references ordenServicio(idOrdenServicio),
	constraint fk_pedidoMaterial_compra foreign key (idCompra)
	references compra(idCompra)
);

create table detalleOrdenServicio(
	idDetalleOrdenServicio int primary key,
	idOrdenServicio int,
	idTrabajo int,
	precioCobrado DECIMAL(10,2) NOT NULL,
	notaTecnica nvarchar(100),
	constraint fk_detalleOrdenServicio_ordenServicio
	foreign key (idOrdenServicio)
	references ordenServicio(idOrdenServicio),
	constraint fk_detalleOrdenServicio_trabajo
	foreign key (idTrabajo)
	references trabajo(idTrabajo)
);

create table reparacionMat(
	idReparacionMat int primary key,
	idOrdenServicio int,
	idLoteAlmacen int,
	cantida int,
	precioUnitario DECIMAL(10,2) NOT NULL,
	constraint fk_reparacionMat_ordenServicio
	foreign key (idOrdenServicio)
	references ordenServicio(idOrdenServicio),
	constraint fk_reparacionMat foreign key (idLoteAlmacen)
	references LoteAlmacen(idLoteAlmacen)
);
