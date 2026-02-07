import pyodbc
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, mean_squared_error, r2_score, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

# Configuración de estilo
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Configuración de conexión
server = 'localhost'
database = 'PROYECTO'

conn = pyodbc.connect(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"Trusted_Connection=yes;"
)

print("="*80)
print("           MINERÍA DE DATOS - TIENDA DE ELECTRÓNICA")
print("="*80)
print()

# ============================================================================
# EXTRACCIÓN DE DATOS
# ============================================================================

print("📊 Extrayendo datos de la base de datos...")
print()

# Query 1: Datos de clientes (para K-Means)
query_clientes = """
SELECT 
    c.idCliente,
    c.nombre + ' ' + c.apellidoP as nombreCompleto,
    COUNT(DISTINCT v.idVenta) as cantidadCompras,
    SUM(v.total) as totalGastado,
    AVG(v.total) as ticketPromedio,
    COUNT(DISTINCT p.idProducto) as productosDistintos,
    DATEDIFF(day, MIN(v.fecha), MAX(v.fecha)) as diasComoCliente,
    MAX(v.fecha) as ultimaCompra
FROM cliente c
INNER JOIN venta v ON c.idCliente = v.idCliente
INNER JOIN ventaDetalle vd ON v.idVenta = vd.idVenta
INNER JOIN loteAlmacen la ON vd.idLoteAlmacen = la.idLoteAlmacen
INNER JOIN lote l ON la.idLote = l.idLote
INNER JOIN producto p ON l.idProducto = p.idProducto
WHERE v.estado = 'COMPLETADA'
GROUP BY c.idCliente, c.nombre, c.apellidoP
HAVING COUNT(DISTINCT v.idVenta) > 0
"""
df_clientes = pd.read_sql(query_clientes, conn)
print(f"✅ Datos de clientes: {len(df_clientes)} registros")

# Query 2: Ventas temporales (para Regresión Lineal)
query_ventas_tiempo = """
SELECT 
    CONVERT(DATE, v.fecha) as fecha,
    COUNT(v.idVenta) as cantidadVentas,
    SUM(v.total) as totalVentas,
    AVG(v.total) as ventaPromedio,
    DATEPART(MONTH, v.fecha) as mes,
    DATEPART(YEAR, v.fecha) as anio,
    DATEPART(WEEKDAY, v.fecha) as diaSemana,
    DATEPART(DAY, v.fecha) as dia
FROM venta v
WHERE v.estado = 'COMPLETADA'
GROUP BY CONVERT(DATE, v.fecha), DATEPART(MONTH, v.fecha), 
         DATEPART(YEAR, v.fecha), DATEPART(WEEKDAY, v.fecha),
         DATEPART(DAY, v.fecha)
ORDER BY fecha
"""
df_ventas_tiempo = pd.read_sql(query_ventas_tiempo, conn)
print(f"✅ Ventas temporales: {len(df_ventas_tiempo)} registros")

# Query 3: Info adicional para contexto
query_resumen = """
SELECT 
    COUNT(DISTINCT c.idCliente) as totalClientes,
    COUNT(DISTINCT v.idVenta) as totalVentas,
    SUM(v.total) as ventasTotales,
    AVG(v.total) as ventaPromedio
FROM venta v
INNER JOIN cliente c ON v.idCliente = c.idCliente
WHERE v.estado = 'COMPLETADA'
"""
df_resumen = pd.read_sql(query_resumen, conn)
print(f"✅ Resumen general: {len(df_resumen)} registros")

conn.close()
print("\n✅ Extracción de datos completada\n")

# Mostrar resumen del negocio
print("="*80)
print("📈 RESUMEN DEL NEGOCIO")
print("="*80)
print(f"Total de Clientes: {df_resumen['totalClientes'].values[0]:,}")
print(f"Total de Ventas: {df_resumen['totalVentas'].values[0]:,}")
print(f"Ventas Totales: ${df_resumen['ventasTotales'].values[0]:,.2f}")
print(f"Ticket Promedio: ${df_resumen['ventaPromedio'].values[0]:,.2f}")
print()

# ============================================================================
# MODELO 1: K-MEANS - SEGMENTACIÓN DE CLIENTES (RFM)
# ============================================================================

print("="*80)
print("🎯 MODELO 1: K-MEANS - SEGMENTACIÓN DE CLIENTES")
print("="*80)
print()

# Preparar datos
df_clientes_ml = df_clientes.copy()

# Calcular Recency (días desde última compra)
fecha_referencia = df_clientes_ml['ultimaCompra'].max()
fecha_referencia = pd.to_datetime(fecha_referencia)
df_clientes_ml['ultimaCompra'] = pd.to_datetime(df_clientes_ml['ultimaCompra'])
df_clientes_ml['recency'] = (fecha_referencia - df_clientes_ml['ultimaCompra']).dt.days

# Crear features RFM
features_rfm = ['recency', 'cantidadCompras', 'totalGastado', 'ticketPromedio']
X_clientes = df_clientes_ml[features_rfm].fillna(0)

# Normalizar datos
scaler = StandardScaler()
X_clientes_scaled = scaler.fit_transform(X_clientes)

# Método del codo para encontrar K óptimo
print("🔍 Buscando número óptimo de clusters...")
inertias = []
silhouette_scores = []
K_range = range(2, 9)

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_clientes_scaled)
    inertias.append(kmeans.inertia_)
    silhouette_scores.append(silhouette_score(X_clientes_scaled, kmeans.labels_))

# Encontrar el K óptimo (mayor silhouette score)
k_optimo = K_range[np.argmax(silhouette_scores)]
print(f"✅ K óptimo encontrado: {k_optimo}")
print()

# Aplicar K-Means con K óptimo
kmeans_final = KMeans(n_clusters=k_optimo, random_state=42, n_init=10)
df_clientes_ml['cluster'] = kmeans_final.fit_predict(X_clientes_scaled)

# Calcular métricas
silhouette_avg = silhouette_score(X_clientes_scaled, df_clientes_ml['cluster'])
inertia_final = kmeans_final.inertia_

print("📊 MÉTRICAS DEL MODELO K-MEANS:")
print("-" * 80)
print(f"Número de Clusters: {k_optimo}")
print(f"Silhouette Score: {silhouette_avg:.4f} (Rango: -1 a 1, mejor cerca de 1)")
print(f"Inercia: {inertia_final:,.2f} (Menor es mejor)")
print(f"Clientes analizados: {len(df_clientes_ml):,}")
print()

# Analizar y etiquetar cada cluster
print("="*80)
print("📊 CARACTERÍSTICAS DE CADA SEGMENTO DE CLIENTES")
print("="*80)

etiquetas_clusters = []
descripciones_clusters = []

for i in range(k_optimo):
    cluster_data = df_clientes_ml[df_clientes_ml['cluster'] == i]
    
    # Calcular promedios
    avg_recency = cluster_data['recency'].mean()
    avg_compras = cluster_data['cantidadCompras'].mean()
    avg_gastado = cluster_data['totalGastado'].mean()
    avg_ticket = cluster_data['ticketPromedio'].mean()
    
    # Etiquetar cluster según características
    if avg_gastado > df_clientes_ml['totalGastado'].quantile(0.75) and avg_compras > df_clientes_ml['cantidadCompras'].median():
        etiqueta = "VIP - Alto Valor"
        descripcion = "Clientes con alto gasto y alta frecuencia"
    elif avg_compras > df_clientes_ml['cantidadCompras'].quantile(0.75):
        etiqueta = "Frecuentes"
        descripcion = "Clientes con alta frecuencia de compra"
    elif avg_gastado > df_clientes_ml['totalGastado'].median():
        etiqueta = "Alto Ticket"
        descripcion = "Clientes con compras de alto valor"
    elif avg_recency < df_clientes_ml['recency'].median():
        etiqueta = "Activos Recientes"
        descripcion = "Clientes con compras recientes"
    else:
        etiqueta = "En Riesgo"
        descripcion = "Clientes con baja actividad reciente"
    
    etiquetas_clusters.append(etiqueta)
    descripciones_clusters.append(descripcion)
    
    # Imprimir análisis
    print(f"\n🏷️  CLUSTER {i}: {etiqueta}")
    print(f"    📝 {descripcion}")
    print(f"    👥 Cantidad de clientes: {len(cluster_data):,} ({len(cluster_data)/len(df_clientes_ml)*100:.1f}%)")
    print(f"    📅 Recency promedio: {avg_recency:.0f} días")
    print(f"    🔄 Compras promedio: {avg_compras:.1f}")
    print(f"    💰 Total gastado promedio: ${avg_gastado:,.2f}")
    print(f"    🎫 Ticket promedio: ${avg_ticket:,.2f}")
    print(f"    📦 Productos distintos: {cluster_data['productosDistintos'].mean():.1f}")

print()

# Visualizaciones K-Means
fig = plt.figure(figsize=(18, 12))

# Gráfico 1: Método del Codo
ax1 = plt.subplot(3, 3, 1)
ax1.plot(K_range, inertias, 'bo-', linewidth=2.5, markersize=10)
ax1.set_xlabel('Número de Clusters (K)', fontsize=11, fontweight='bold')
ax1.set_ylabel('Inercia', fontsize=11, fontweight='bold')
ax1.set_title('Método del Codo', fontsize=13, fontweight='bold')
ax1.axvline(x=k_optimo, color='red', linestyle='--', linewidth=2, label=f'K óptimo = {k_optimo}')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)

# Gráfico 2: Silhouette Score
ax2 = plt.subplot(3, 3, 2)
ax2.plot(K_range, silhouette_scores, 'ro-', linewidth=2.5, markersize=10)
ax2.set_xlabel('Número de Clusters (K)', fontsize=11, fontweight='bold')
ax2.set_ylabel('Silhouette Score', fontsize=11, fontweight='bold')
ax2.set_title('Calidad de Clustering (Silhouette)', fontsize=13, fontweight='bold')
ax2.axvline(x=k_optimo, color='blue', linestyle='--', linewidth=2, label=f'K óptimo = {k_optimo}')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)

# Gráfico 3: Distribución de clientes por cluster
ax3 = plt.subplot(3, 3, 3)
cluster_counts = df_clientes_ml['cluster'].value_counts().sort_index()
colors = plt.cm.Set3(range(k_optimo))
bars = ax3.bar(range(k_optimo), cluster_counts.values, color=colors, edgecolor='black', linewidth=1.5)
ax3.set_xlabel('Cluster', fontsize=11, fontweight='bold')
ax3.set_ylabel('Cantidad de Clientes', fontsize=11, fontweight='bold')
ax3.set_title('Distribución de Clientes por Segmento', fontsize=13, fontweight='bold')
ax3.set_xticks(range(k_optimo))
ax3.set_xticklabels([f'C{i}\n{etiquetas_clusters[i][:12]}...' for i in range(k_optimo)], 
                     rotation=20, ha='right', fontsize=9)
ax3.grid(True, alpha=0.3, axis='y')
# Agregar valores
for bar in bars:
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height)}',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

# Gráfico 4: Recency vs Total Gastado
ax4 = plt.subplot(3, 3, 4)
scatter = ax4.scatter(df_clientes_ml['recency'], 
                     df_clientes_ml['totalGastado'],
                     c=df_clientes_ml['cluster'], 
                     cmap='viridis', s=100, alpha=0.6, edgecolors='black', linewidth=0.5)
ax4.set_xlabel('Recency (días desde última compra)', fontsize=11, fontweight='bold')
ax4.set_ylabel('Total Gastado ($)', fontsize=11, fontweight='bold')
ax4.set_title('Segmentación: Recency vs Gasto Total', fontsize=13, fontweight='bold')
ax4.grid(True, alpha=0.3)
plt.colorbar(scatter, ax=ax4, label='Cluster')

# Gráfico 5: Cantidad de Compras vs Total Gastado
ax5 = plt.subplot(3, 3, 5)
scatter2 = ax5.scatter(df_clientes_ml['cantidadCompras'], 
                      df_clientes_ml['totalGastado'],
                      c=df_clientes_ml['cluster'], 
                      cmap='viridis', s=100, alpha=0.6, edgecolors='black', linewidth=0.5)
ax5.set_xlabel('Cantidad de Compras', fontsize=11, fontweight='bold')
ax5.set_ylabel('Total Gastado ($)', fontsize=11, fontweight='bold')
ax5.set_title('Segmentación: Frecuencia vs Gasto', fontsize=13, fontweight='bold')
ax5.grid(True, alpha=0.3)
plt.colorbar(scatter2, ax=ax5, label='Cluster')

# Gráfico 6: Ticket Promedio por Cluster
ax6 = plt.subplot(3, 3, 6)
ticket_promedio = df_clientes_ml.groupby('cluster')['ticketPromedio'].mean().sort_index()
bars2 = ax6.bar(range(k_optimo), ticket_promedio.values, color=colors, edgecolor='black', linewidth=1.5)
ax6.set_xlabel('Cluster', fontsize=11, fontweight='bold')
ax6.set_ylabel('Ticket Promedio ($)', fontsize=11, fontweight='bold')
ax6.set_title('Ticket Promedio por Segmento', fontsize=13, fontweight='bold')
ax6.set_xticks(range(k_optimo))
ax6.set_xticklabels([f'C{i}' for i in range(k_optimo)])
ax6.grid(True, alpha=0.3, axis='y')
for bar in bars2:
    height = bar.get_height()
    ax6.text(bar.get_x() + bar.get_width()/2., height,
            f'${height:.0f}',
            ha='center', va='bottom', fontsize=9, fontweight='bold')

# Gráfico 7: Box plot de Total Gastado por Cluster
ax7 = plt.subplot(3, 3, 7)
cluster_data_list = [df_clientes_ml[df_clientes_ml['cluster'] == i]['totalGastado'].values 
                     for i in range(k_optimo)]
bp = ax7.boxplot(cluster_data_list, labels=[f'C{i}' for i in range(k_optimo)],
                patch_artist=True)
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
ax7.set_xlabel('Cluster', fontsize=11, fontweight='bold')
ax7.set_ylabel('Total Gastado ($)', fontsize=11, fontweight='bold')
ax7.set_title('Distribución de Gasto por Segmento', fontsize=13, fontweight='bold')
ax7.grid(True, alpha=0.3, axis='y')

# Gráfico 8: Heatmap de características promedio
ax8 = plt.subplot(3, 3, 8)
heatmap_data = df_clientes_ml.groupby('cluster')[features_rfm].mean()
# Normalizar para mejor visualización
heatmap_data_norm = (heatmap_data - heatmap_data.min()) / (heatmap_data.max() - heatmap_data.min())
sns.heatmap(heatmap_data_norm.T, annot=True, fmt='.2f', cmap='YlOrRd', 
            xticklabels=[f'C{i}' for i in range(k_optimo)],
            yticklabels=['Recency', 'Compras', 'Total $', 'Ticket'],
            ax=ax8, cbar_kws={'label': 'Valor Normalizado'})
ax8.set_xlabel('Cluster', fontsize=11, fontweight='bold')
ax8.set_title('Perfil Promedio por Segmento (Normalizado)', fontsize=13, fontweight='bold')

# Gráfico 9: Valor total por cluster
ax9 = plt.subplot(3, 3, 9)
valor_cluster = df_clientes_ml.groupby('cluster')['totalGastado'].sum().sort_index()
bars3 = ax9.bar(range(k_optimo), valor_cluster.values, color=colors, edgecolor='black', linewidth=1.5)
ax9.set_xlabel('Cluster', fontsize=11, fontweight='bold')
ax9.set_ylabel('Valor Total del Segmento ($)', fontsize=11, fontweight='bold')
ax9.set_title('Valor Total Generado por Segmento', fontsize=13, fontweight='bold')
ax9.set_xticks(range(k_optimo))
ax9.set_xticklabels([f'C{i}\n{etiquetas_clusters[i][:12]}...' for i in range(k_optimo)], 
                    rotation=20, ha='right', fontsize=9)
ax9.grid(True, alpha=0.3, axis='y')
for bar in bars3:
    height = bar.get_height()
    ax9.text(bar.get_x() + bar.get_width()/2., height,
            f'${height/1000:.0f}K',
            ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.suptitle('ANÁLISIS DE SEGMENTACIÓN DE CLIENTES - K-MEANS CLUSTERING', 
             fontsize=16, fontweight='bold', y=0.995)
plt.tight_layout()
plt.savefig('01_kmeans_segmentacion_clientes.png', dpi=300, bbox_inches='tight')
plt.show()

print("💾 Gráfico guardado: 01_kmeans_segmentacion_clientes.png\n")

# ============================================================================
# MODELO 2: REGRESIÓN LINEAL - PREDICCIÓN DE VENTAS
# ============================================================================

print("="*80)
print("📈 MODELO 2: REGRESIÓN LINEAL - PREDICCIÓN DE VENTAS")
print("="*80)
print()

# Preparar datos
df_ventas_ml = df_ventas_tiempo.copy()
df_ventas_ml['fecha'] = pd.to_datetime(df_ventas_ml['fecha'])
df_ventas_ml = df_ventas_ml.sort_values('fecha')

# Crear features temporales
df_ventas_ml['dia_num'] = (df_ventas_ml['fecha'] - df_ventas_ml['fecha'].min()).dt.days
df_ventas_ml['mes_sin'] = np.sin(2 * np.pi * df_ventas_ml['mes'] / 12)
df_ventas_ml['mes_cos'] = np.cos(2 * np.pi * df_ventas_ml['mes'] / 12)
df_ventas_ml['semana_sin'] = np.sin(2 * np.pi * df_ventas_ml['diaSemana'] / 7)
df_ventas_ml['semana_cos'] = np.cos(2 * np.pi * df_ventas_ml['diaSemana'] / 7)
df_ventas_ml['es_inicio_mes'] = (df_ventas_ml['dia'] <= 10).astype(int)
df_ventas_ml['es_fin_mes'] = (df_ventas_ml['dia'] >= 20).astype(int)

# Media móvil de 7 días
df_ventas_ml['media_movil_7'] = df_ventas_ml['totalVentas'].rolling(window=7, min_periods=1).mean()

# Features y target
features = ['dia_num', 'mes_sin', 'mes_cos', 'semana_sin', 'semana_cos',
            'cantidadVentas', 'es_inicio_mes', 'es_fin_mes', 'media_movil_7']
X = df_ventas_ml[features].fillna(0)
y = df_ventas_ml['totalVentas']

# Split temporal (últimos 20% para test)
split_idx = int(len(X) * 0.8)
X_train, X_test = X[:split_idx], X[split_idx:]
y_train, y_test = y[:split_idx], y[split_idx:]

print(f"📊 Datos de entrenamiento: {len(X_train)} días")
print(f"📊 Datos de prueba: {len(X_test)} días")
print()

# Entrenar modelo
modelo_regresion = LinearRegression()
modelo_regresion.fit(X_train, y_train)

# Predicciones
y_pred_train = modelo_regresion.predict(X_train)
y_pred_test = modelo_regresion.predict(X_test)

# Calcular métricas
r2_train = r2_score(y_train, y_pred_train)
r2_test = r2_score(y_test, y_pred_test)
rmse_train = np.sqrt(mean_squared_error(y_train, y_pred_train))
rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))
mae_train = mean_absolute_error(y_train, y_pred_train)
mae_test = mean_absolute_error(y_test, y_pred_test)
mape_test = np.mean(np.abs((y_test - y_pred_test) / y_test)) * 100

print("="*80)
print("📊 MÉTRICAS DEL MODELO DE REGRESIÓN LINEAL")
print("="*80)
print("\n📈 CONJUNTO DE ENTRENAMIENTO:")
print(f"  R² (Coeficiente de Determinación): {r2_train:.4f}")
print(f"  RMSE (Error Cuadrático Medio): ${rmse_train:,.2f}")
print(f"  MAE (Error Absoluto Medio): ${mae_train:,.2f}")

print("\n📊 CONJUNTO DE PRUEBA:")
print(f"  R² (Coeficiente de Determinación): {r2_test:.4f}")
print(f"  RMSE (Error Cuadrático Medio): ${rmse_test:,.2f}")
print(f"  MAE (Error Absoluto Medio): ${mae_test:,.2f}")
print(f"  MAPE (Error Porcentual Absoluto): {mape_test:.2f}%")

print("\n📝 INTERPRETACIÓN:")
if r2_test > 0.7:
    print(f"  ✅ Excelente ajuste (R² = {r2_test:.2f})")
elif r2_test > 0.5:
    print(f"  ✓ Buen ajuste (R² = {r2_test:.2f})")
else:
    print(f"  ⚠ Ajuste moderado (R² = {r2_test:.2f})")
print(f"  💡 El modelo explica el {r2_test*100:.1f}% de la variabilidad en las ventas")
print(f"  💡 Error promedio en predicción: ${mae_test:,.2f} ({mape_test:.1f}%)")
print()

# Importancia de features
importancia = pd.DataFrame({
    'Feature': features,
    'Coeficiente': modelo_regresion.coef_,
    'Impacto_Abs': np.abs(modelo_regresion.coef_)
}).sort_values('Impacto_Abs', ascending=False)

print("="*80)
print("🎯 IMPORTANCIA DE VARIABLES (TOP 5)")
print("="*80)
for idx, row in importancia.head(5).iterrows():
    direccion = "↑ Aumenta" if row['Coeficiente'] > 0 else "↓ Disminuye"
    print(f"{row['Feature']:20s}: {direccion} las ventas en ${abs(row['Coeficiente']):,.2f}")
print()

# Predicción para próximos días
dias_futuro = 30
ultimo_dia = df_ventas_ml['dia_num'].max()
fechas_futuras = pd.date_range(start=df_ventas_ml['fecha'].max() + pd.Timedelta(days=1), 
                                periods=dias_futuro)

X_futuro = pd.DataFrame({
    'dia_num': range(ultimo_dia + 1, ultimo_dia + dias_futuro + 1),
    'mes_sin': np.sin(2 * np.pi * fechas_futuras.month / 12),
    'mes_cos': np.cos(2 * np.pi * fechas_futuras.month / 12),
    'semana_sin': np.sin(2 * np.pi * fechas_futuras.dayofweek / 7),
    'semana_cos': np.cos(2 * np.pi * fechas_futuras.dayofweek / 7),
    'cantidadVentas': df_ventas_ml['cantidadVentas'].median(),
    'es_inicio_mes': (fechas_futuras.day <= 10).astype(int),
    'es_fin_mes': (fechas_futuras.day >= 20).astype(int),
    'media_movil_7': df_ventas_ml['media_movil_7'].iloc[-1]
})

y_pred_futuro = modelo_regresion.predict(X_futuro)

print(f"💰 PROYECCIÓN DE VENTAS - Próximos {dias_futuro} días:")
print(f"   Total proyectado: ${y_pred_futuro.sum():,.2f}")
print(f"   Promedio diario: ${y_pred_futuro.mean():,.2f}")
print(f"   Rango: ${y_pred_futuro.min():,.2f} - ${y_pred_futuro.max():,.2f}")
print()

# Visualizaciones Regresión Lineal
fig = plt.figure(figsize=(18, 12))

# Gráfico 1: Valores reales vs predichos (Test)
ax1 = plt.subplot(3, 3, 1)
ax1.scatter(y_test, y_pred_test, alpha=0.6, s=80, edgecolors='black', linewidth=0.5, color='steelblue')
ax1.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 
        'r--', lw=3, label='Predicción Perfecta')
ax1.set_xlabel('Ventas Reales ($)', fontsize=11, fontweight='bold')
ax1.set_ylabel('Ventas Predichas ($)', fontsize=11, fontweight='bold')
ax1.set_title(f'Predicción vs Real - Test\n(R² = {r2_test:.3f})', fontsize=12, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)

# Gráfico 2: Residuos
ax2 = plt.subplot(3, 3, 2)
residuos = y_test.values - y_pred_test
ax2.scatter(y_pred_test, residuos, alpha=0.6, s=80, edgecolors='black', 
           linewidth=0.5, color='coral')
ax2.axhline(y=0, color='red', linestyle='--', lw=3)
ax2.set_xlabel('Ventas Predichas ($)', fontsize=11, fontweight='bold')
ax2.set_ylabel('Residuos ($)', fontsize=11, fontweight='bold')
ax2.set_title('Análisis de Residuos', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3)

# Gráfico 3: Distribución de residuos
ax3 = plt.subplot(3, 3, 3)
ax3.hist(residuos, bins=30, edgecolor='black', alpha=0.7, color='lightgreen')
ax3.axvline(x=0, color='red', linestyle='--', lw=2)
ax3.set_xlabel('Residuo ($)', fontsize=11, fontweight='bold')
ax3.set_ylabel('Frecuencia', fontsize=11, fontweight='bold')
ax3.set_title('Distribución de Residuos', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='y')

# Gráfico 4: Serie temporal completa
ax4 = plt.subplot(3, 1, 2)
dias_train = df_ventas_ml.iloc[:split_idx]['dia_num'].values
dias_test = df_ventas_ml.iloc[split_idx:]['dia_num'].values
ax4.plot(dias_train, y_train, 'o-', label='Entrenamiento (Real)', 
        alpha=0.6, linewidth=1.5, markersize=4, color='blue')
ax4.plot(dias_test, y_test, 'o-', label='Prueba (Real)', 
        alpha=0.6, linewidth=1.5, markersize=4, color='green')
ax4.plot(dias_test, y_pred_test, 's-', label='Predicción', 
        alpha=0.8, linewidth=2, markersize=5, color='red')
ax4.set_xlabel('Días desde inicio', fontsize=11, fontweight='bold')
ax4.set_ylabel('Total Ventas ($)', fontsize=11, fontweight='bold')
ax4.set_title('Serie Temporal: Ventas Reales vs Predicción', fontsize=13, fontweight='bold')
ax4.legend(fontsize=10)
ax4.grid(True, alpha=0.3)

# Gráfico 5: Proyección futura
ax5 = plt.subplot(3, 3, 7)
# Últimos 60 días reales
ultimos_dias = df_ventas_ml.tail(60)
ax5.plot(ultimos_dias['dia_num'], ultimos_dias['totalVentas'], 
        'o-', label='Histórico', alpha=0.7, linewidth=2, markersize=5, color='blue')
ax5.plot(X_futuro['dia_num'], y_pred_futuro, 
        's-', label='Proyección', alpha=0.8, linewidth=2.5, markersize=6, color='orange')
ax5.axvline(x=ultimo_dia, color='red', linestyle='--', lw=2, label='Hoy', alpha=0.7)
ax5.set_xlabel('Días desde inicio', fontsize=11, fontweight='bold')
ax5.set_ylabel('Total Ventas ($)', fontsize=11, fontweight='bold')
ax5.set_title(f'Proyección - Próximos {dias_futuro} días', fontsize=12, fontweight='bold')
ax5.legend(fontsize=9)
ax5.grid(True, alpha=0.3)

# Gráfico 6: Importancia de features
ax6 = plt.subplot(3, 3, 8)
importancia_plot = importancia.sort_values('Coeficiente')
colors_feat = ['red' if x < 0 else 'green' for x in importancia_plot['Coeficiente']]
ax6.barh(importancia_plot['Feature'], importancia_plot['Coeficiente'], color=colors_feat, edgecolor='black')
ax6.set_xlabel('Coeficiente', fontsize=11, fontweight='bold')
ax6.set_title('Importancia de Variables', fontsize=12, fontweight='bold')
ax6.axvline(x=0, color='black', linestyle='-', linewidth=1.5)
ax6.grid(True, alpha=0.3, axis='x')

# Gráfico 7: Métricas comparativas
ax7 = plt.subplot(3, 3, 9)
metricas_nombres = ['R²', 'RMSE\n(miles)', 'MAE\n(miles)', 'MAPE\n(%)']
metricas_train = [r2_train, rmse_train/1000, mae_train/1000, mape_test]
metricas_test = [r2_test, rmse_test/1000, mae_test/1000, mape_test]

x_pos = np.arange(len(metricas_nombres))
width = 0.35

bars1 = ax7.bar(x_pos - width/2, metricas_train[:len(metricas_nombres)], 
               width, label='Train', color='skyblue', edgecolor='black')
bars2 = ax7.bar(x_pos + width/2, metricas_test[:len(metricas_nombres)], 
               width, label='Test', color='lightcoral', edgecolor='black')

ax7.set_ylabel('Valor', fontsize=11, fontweight='bold')
ax7.set_title('Comparación de Métricas', fontsize=12, fontweight='bold')
ax7.set_xticks(x_pos)
ax7.set_xticklabels(metricas_nombres, fontsize=9)
ax7.legend(fontsize=10)
ax7.grid(True, alpha=0.3, axis='y')

plt.suptitle('ANÁLISIS DE PREDICCIÓN DE VENTAS - REGRESIÓN LINEAL', 
             fontsize=16, fontweight='bold', y=0.995)
plt.tight_layout()
plt.savefig('02_regresion_lineal_ventas.png', dpi=300, bbox_inches='tight')
plt.show()

print("💾 Gráfico guardado: 02_regresion_lineal_ventas.png\n")

# ============================================================================
# RESUMEN FINAL
# ============================================================================

print("\n" + "="*80)
print("🎉 RESUMEN FINAL - MINERÍA DE DATOS")
print("="*80)
print()
print("✅ MODELO 1: K-MEANS - SEGMENTACIÓN DE CLIENTES")
print(f"   • Clusters creados: {k_optimo}")
print(f"   • Silhouette Score: {silhouette_avg:.4f}")
print(f"   • Clientes segmentados: {len(df_clientes_ml):,}")
print(f"   • Mejor segmento: {etiquetas_clusters[df_clientes_ml.groupby('cluster')['totalGastado'].sum().idxmax()]}")
print()
print("✅ MODELO 2: REGRESIÓN LINEAL - PREDICCIÓN DE VENTAS")
print(f"   • R² en Test: {r2_test:.4f} ({r2_test*100:.1f}% de varianza explicada)")
print(f"   • Error promedio (MAE): ${mae_test:,.2f}")
print(f"   • Error porcentual (MAPE): {mape_test:.2f}%")
print(f"   • Proyección {dias_futuro} días: ${y_pred_futuro.sum():,.2f}")
print()
print("📁 ARCHIVOS GENERADOS:")
print("   • 01_kmeans_segmentacion_clientes.png")
print("   • 02_regresion_lineal_ventas.png")
print()
print("="*80)
print("✨ ANÁLISIS COMPLETADO EXITOSAMENTE ✨")
print("="*80)