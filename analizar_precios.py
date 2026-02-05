"""
📊 Renfe Price Tracker - Script de análisis
============================================
Ejecuta este script localmente (o en Colab) para analizar los datos recogidos.

Uso:
    python analizar_precios.py

O copia las celdas a un notebook de Colab.
"""

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

ARCHIVO_DATOS = "data/precios_historico.csv"

DIAS_SEMANA_ORDEN = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']


# =============================================================================
# CARGAR DATOS
# =============================================================================

def cargar_datos():
    """Carga y prepara los datos."""
    if not os.path.exists(ARCHIVO_DATOS):
        print(f"❌ No se encontró el archivo: {ARCHIVO_DATOS}")
        print("   Asegúrate de haber ejecutado recoger_precios.py primero")
        return None
    
    df = pd.read_csv(ARCHIVO_DATOS)
    df['timestamp_consulta'] = pd.to_datetime(df['timestamp_consulta'])
    df['fecha_viaje'] = pd.to_datetime(df['fecha_viaje'])
    
    print(f"✅ Datos cargados: {len(df)} registros")
    print(f"   Desde: {df['timestamp_consulta'].min()}")
    print(f"   Hasta: {df['timestamp_consulta'].max()}")
    print(f"   Días de recogida: {df['timestamp_consulta'].dt.date.nunique()}")
    
    return df


# =============================================================================
# ANÁLISIS 1: Resumen general
# =============================================================================

def resumen_general(df):
    """Muestra un resumen general de los datos."""
    print("\n" + "=" * 60)
    print("📊 RESUMEN GENERAL")
    print("=" * 60)
    
    for ruta in df['ruta'].unique():
        df_ruta = df[df['ruta'] == ruta]
        print(f"\n🚂 Ruta: {ruta}")
        print(f"   Registros: {len(df_ruta)}")
        print(f"   Precio mínimo: {df_ruta['precio'].min():.2f}€")
        print(f"   Precio medio: {df_ruta['precio'].mean():.2f}€")
        print(f"   Precio máximo: {df_ruta['precio'].max():.2f}€")


# =============================================================================
# ANÁLISIS 2: Evolución del precio de un tren específico
# =============================================================================

def evolucion_precio_tren(df, fecha_viaje, hora_salida, ruta=None):
    """
    Muestra cómo ha evolucionado el precio de un tren específico
    a lo largo de los días de recogida.
    """
    filtro = (df['fecha_viaje'] == pd.to_datetime(fecha_viaje)) & \
             (df['hora_salida'] == hora_salida)
    
    if ruta:
        filtro = filtro & (df['ruta'] == ruta)
    
    df_tren = df[filtro].sort_values('timestamp_consulta')
    
    if len(df_tren) == 0:
        print(f"❌ No se encontraron datos para {fecha_viaje} {hora_salida}")
        return
    
    print(f"\n📈 Evolución del precio: {fecha_viaje} a las {hora_salida}")
    print("-" * 50)
    
    for _, row in df_tren.iterrows():
        fecha_consulta = row['timestamp_consulta'].strftime('%Y-%m-%d')
        print(f"   {fecha_consulta} ({row['dias_antelacion']:2d} días antes): {row['precio']:.2f}€")
    
    # Gráfico
    if len(df_tren) > 1:
        plt.figure(figsize=(10, 5))
        plt.plot(df_tren['dias_antelacion'], df_tren['precio'], 'bo-', linewidth=2, markersize=8)
        plt.xlabel('Días de antelación')
        plt.ylabel('Precio (€)')
        plt.title(f'Evolución del precio: {fecha_viaje} {hora_salida}')
        plt.gca().invert_xaxis()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'evolucion_{fecha_viaje}_{hora_salida.replace(":", "")}.png', dpi=150)
        plt.show()


# =============================================================================
# ANÁLISIS 3: Top 3 precios mínimos por día de la semana
# =============================================================================

def top3_por_dia(df, ruta=None):
    """Muestra los 3 mejores precios para cada día de la semana."""
    
    if ruta:
        df = df[df['ruta'] == ruta]
        print(f"\n🚂 Ruta: {ruta}")
    
    print("\n" + "=" * 60)
    print("🏆 TOP 3 PRECIOS MÍNIMOS POR DÍA DE LA SEMANA")
    print("=" * 60)
    
    for dia in DIAS_SEMANA_ORDEN:
        df_dia = df[df['dia_semana'] == dia]
        
        if len(df_dia) == 0:
            continue
        
        top3 = df_dia.nsmallest(3, 'precio')
        
        print(f"\n📅 {dia.upper()}")
        print("-" * 50)
        
        for i, (_, row) in enumerate(top3.iterrows(), 1):
            fecha = row['fecha_viaje'].strftime('%Y-%m-%d') if hasattr(row['fecha_viaje'], 'strftime') else row['fecha_viaje']
            print(f"   {i}. {row['precio']:.2f}€ | {fecha} | "
                  f"{row['dias_antelacion']} días antes | {row['hora_salida']} | {row['tipo_tren']}")


# =============================================================================
# ANÁLISIS 4: ¿Cuándo comprar? Precio medio por antelación
# =============================================================================

def precio_por_antelacion(df, ruta=None):
    """Analiza el precio medio según los días de antelación."""
    
    if ruta:
        df = df[df['ruta'] == ruta]
    
    print("\n" + "=" * 60)
    print("📈 PRECIO SEGÚN DÍAS DE ANTELACIÓN")
    print("=" * 60)
    
    stats = df.groupby('dias_antelacion')['precio'].agg(['min', 'mean', 'max', 'count'])
    stats = stats.round(2)
    
    # Encontrar el mejor momento para comprar
    mejor_media = stats['mean'].idxmin()
    mejor_min = stats['min'].idxmin()
    
    print(f"\n💡 CONCLUSIONES:")
    print(f"   Mejor precio MEDIO: {mejor_media} días antes ({stats.loc[mejor_media, 'mean']:.2f}€)")
    print(f"   Mejor precio MÍNIMO: {mejor_min} días antes ({stats.loc[mejor_min, 'min']:.2f}€)")
    
    print(f"\n📊 Tabla completa:")
    print(stats.to_string())
    
    # Gráfico
    plt.figure(figsize=(12, 6))
    
    plt.fill_between(stats.index, stats['min'], stats['max'], alpha=0.3, label='Rango min-max')
    plt.plot(stats.index, stats['mean'], 'b-', linewidth=2, label='Precio medio')
    plt.plot(stats.index, stats['min'], 'g--', linewidth=1, label='Precio mínimo')
    
    plt.xlabel('Días de antelación')
    plt.ylabel('Precio (€)')
    plt.title('Precio según días de antelación')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.gca().invert_xaxis()
    
    plt.tight_layout()
    plt.savefig('precio_vs_antelacion.png', dpi=150)
    plt.show()
    
    return stats


# =============================================================================
# ANÁLISIS 5: Comparativa por día de la semana
# =============================================================================

def precio_por_dia_semana(df, ruta=None):
    """Compara precios entre días de la semana."""
    
    if ruta:
        df = df[df['ruta'] == ruta]
    
    print("\n" + "=" * 60)
    print("📅 PRECIO POR DÍA DE LA SEMANA")
    print("=" * 60)
    
    stats = df.groupby('dia_semana')['precio'].agg(['min', 'mean', 'max', 'count'])
    stats = stats.reindex(DIAS_SEMANA_ORDEN)
    stats = stats.round(2)
    
    print(stats.to_string())
    
    # Gráfico
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = range(len(stats))
    ax.bar(x, stats['mean'], alpha=0.7, color='steelblue')
    ax.errorbar(x, stats['mean'], 
                yerr=[stats['mean'] - stats['min'], stats['max'] - stats['mean']], 
                fmt='none', color='black', capsize=5)
    
    ax.set_xticks(x)
    ax.set_xticklabels(stats.index, rotation=45)
    ax.set_ylabel('Precio (€)')
    ax.set_title('Precio por día de la semana')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('precio_por_dia.png', dpi=150)
    plt.show()
    
    return stats


# =============================================================================
# ANÁLISIS 6: Heatmap completo
# =============================================================================

def heatmap_precios(df, ruta=None):
    """Genera un heatmap de precios por día de semana y antelación."""
    
    if ruta:
        df = df[df['ruta'] == ruta]
    
    # Crear tabla pivote
    pivot = df.pivot_table(
        values='precio', 
        index='dias_antelacion', 
        columns='dia_semana', 
        aggfunc='min'
    )
    pivot = pivot[[d for d in DIAS_SEMANA_ORDEN if d in pivot.columns]]
    
    # Gráfico
    fig, ax = plt.subplots(figsize=(12, 10))
    
    im = ax.imshow(pivot.values, cmap='RdYlGn_r', aspect='auto')
    
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha='right')
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    
    ax.set_xlabel('Día de la semana')
    ax.set_ylabel('Días de antelación')
    ax.set_title('Precio mínimo (€) - Verde=barato, Rojo=caro')
    
    # Valores en celdas
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            valor = pivot.iloc[i, j]
            if pd.notna(valor):
                color = 'white' if valor > pivot.values[~pd.isna(pivot.values)].mean() else 'black'
                ax.text(j, i, f'{valor:.0f}', ha='center', va='center', color=color, fontsize=8)
    
    plt.colorbar(im, ax=ax, label='Precio (€)')
    plt.tight_layout()
    plt.savefig('heatmap_precios.png', dpi=150)
    plt.show()


# =============================================================================
# EJECUCIÓN PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    # Cargar datos
    df = cargar_datos()
    
    if df is not None:
        # Ejecutar análisis
        resumen_general(df)
        
        # Análisis por ruta
        for ruta in df['ruta'].unique():
            print(f"\n\n{'='*60}")
            print(f"🚂 ANÁLISIS PARA RUTA: {ruta}")
            print("=" * 60)
            
            top3_por_dia(df, ruta)
            precio_por_antelacion(df, ruta)
            precio_por_dia_semana(df, ruta)
            heatmap_precios(df, ruta)
        
        print("\n\n✅ Análisis completado. Gráficos guardados en el directorio actual.")
