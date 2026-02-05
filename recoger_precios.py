"""
🚄 Renfe Price Tracker - Script de recogida diaria
==================================================
Este script recoge los precios de trenes Renfe para las rutas configuradas
y los acumula en un CSV histórico.

Rutas:
- Barcelona → Valladolid (ida, típicamente viernes)
- Valladolid → Barcelona (vuelta, típicamente domingo)

Autor: Tu nombre
Fecha: 2024
"""

import pandas as pd
from datetime import datetime, timedelta
import time
import os
import sys

# Instalar dependencias si no están
try:
    from renfe_mcp.price_checker import check_prices
except ImportError:
    print("📦 Instalando renfe_mcp...")
    os.system("pip install git+https://github.com/belgrano9/renfe_mcp_server.git -q")
    from renfe_mcp.price_checker import check_prices


# =============================================================================
# CONFIGURACIÓN - Personaliza aquí
# =============================================================================

RUTAS = [
    {"origen": "Barcelona", "destino": "Valladolid", "nombre": "BCN_VLL"},
    {"origen": "Valladolid", "destino": "Barcelona", "nombre": "VLL_BCN"},
]

SEMANAS_ADELANTE = 8  # Cuántas semanas en el futuro consultar
DELAY_ENTRE_CONSULTAS = 2  # Segundos entre peticiones (para no saturar)
ARCHIVO_DATOS = "data/precios_historico.csv"  # Dónde guardar los datos


# =============================================================================
# FUNCIONES
# =============================================================================

DIAS_SEMANA = {
    0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves',
    4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
}


def get_dia_semana(fecha_str):
    """Devuelve el nombre del día de la semana en español."""
    fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
    return DIAS_SEMANA[fecha.weekday()]


def get_fechas_consulta(semanas=8):
    """Genera todas las fechas para las próximas semanas."""
    hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    fechas = []
    
    for i in range(1, semanas * 7 + 1):
        fecha = hoy + timedelta(days=i)
        fechas.append(fecha.strftime("%Y-%m-%d"))
    
    return fechas


def extraer_campo(tren, campos_posibles, default=''):
    """Extrae un campo probando varios nombres posibles."""
    for campo in campos_posibles:
        if isinstance(tren, dict) and campo in tren:
            return tren[campo]
        elif hasattr(tren, campo):
            return getattr(tren, campo)
    return default


def recoger_precios_ruta(origen, destino, fecha):
    """Recoge los precios para una ruta y fecha específica."""
    resultados = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    dia_semana = get_dia_semana(fecha)
    dias_antelacion = (datetime.strptime(fecha, "%Y-%m-%d") - hoy).days
    
    try:
        precios = check_prices(origen, destino, fecha)
        
        if precios:
            for tren in precios:
                precio = extraer_campo(tren, 
                    ['price', 'precio', 'min_price', 'minPrice', 'precioMinimo'], None)
                
                try:
                    precio = float(precio) if precio is not None else None
                except (ValueError, TypeError):
                    precio = None
                
                # Solo guardar si hay precio válido (> 0)
                if precio and precio > 0:
                    resultados.append({
                        'timestamp_consulta': timestamp,
                        'fecha_viaje': fecha,
                        'dia_semana': dia_semana,
                        'dias_antelacion': dias_antelacion,
                        'origen': origen,
                        'destino': destino,
                        'ruta': f"{origen[:3].upper()}_{destino[:3].upper()}",
                        'hora_salida': extraer_campo(tren, 
                            ['departure', 'departure_time', 'salida', 'hora_salida'], ''),
                        'hora_llegada': extraer_campo(tren, 
                            ['arrival', 'arrival_time', 'llegada', 'hora_llegada'], ''),
                        'tipo_tren': extraer_campo(tren, 
                            ['train_type', 'trainType', 'tipo', 'type', 'tren'], ''),
                        'precio': precio,
                        'clase': extraer_campo(tren, 
                            ['class', 'clase', 'travel_class'], 'Turista'),
                    })
        
        return resultados, None
        
    except Exception as e:
        return [], str(e)


def cargar_datos_existentes(archivo):
    """Carga el CSV existente o crea uno vacío."""
    if os.path.exists(archivo):
        try:
            df = pd.read_csv(archivo)
            print(f"📂 Datos existentes cargados: {len(df)} registros")
            return df
        except Exception as e:
            print(f"⚠️ Error cargando datos existentes: {e}")
    
    print("📂 No hay datos previos, empezando desde cero")
    return pd.DataFrame()


def guardar_datos(df, archivo):
    """Guarda el DataFrame en CSV."""
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(archivo), exist_ok=True)
    df.to_csv(archivo, index=False, encoding='utf-8-sig')
    print(f"💾 Datos guardados: {len(df)} registros en {archivo}")


def ejecutar_recogida():
    """Función principal que ejecuta la recogida de precios."""
    print("=" * 60)
    print("🚄 RENFE PRICE TRACKER - Recogida diaria")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Cargar datos existentes
    df_existente = cargar_datos_existentes(ARCHIVO_DATOS)
    
    # Generar fechas a consultar
    fechas = get_fechas_consulta(SEMANAS_ADELANTE)
    print(f"\n📅 Consultando {len(fechas)} fechas ({SEMANAS_ADELANTE} semanas)")
    print(f"   Desde: {fechas[0]} hasta: {fechas[-1]}")
    
    # Recoger precios para cada ruta
    nuevos_registros = []
    errores = []
    
    for ruta in RUTAS:
        origen = ruta["origen"]
        destino = ruta["destino"]
        nombre_ruta = ruta["nombre"]
        
        print(f"\n🚂 Ruta: {origen} → {destino}")
        print("-" * 40)
        
        for i, fecha in enumerate(fechas):
            dia = get_dia_semana(fecha)
            print(f"   [{i+1:2d}/{len(fechas)}] {fecha} ({dia})... ", end="")
            
            resultados, error = recoger_precios_ruta(origen, destino, fecha)
            
            if error:
                print(f"❌ Error")
                errores.append(f"{nombre_ruta} {fecha}: {error}")
            elif resultados:
                print(f"✅ {len(resultados)} trenes")
                nuevos_registros.extend(resultados)
            else:
                print(f"⚠️ Sin disponibilidad")
            
            # Pausa para no saturar
            time.sleep(DELAY_ENTRE_CONSULTAS)
    
    # Combinar con datos existentes
    if nuevos_registros:
        df_nuevo = pd.DataFrame(nuevos_registros)
        
        if len(df_existente) > 0:
            df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
        else:
            df_final = df_nuevo
        
        # Guardar
        guardar_datos(df_final, ARCHIVO_DATOS)
        
        print(f"\n✅ Recogida completada:")
        print(f"   - Nuevos registros: {len(nuevos_registros)}")
        print(f"   - Total acumulado: {len(df_final)}")
    else:
        print("\n⚠️ No se recogieron nuevos registros")
    
    # Mostrar errores si los hubo
    if errores:
        print(f"\n⚠️ Errores ({len(errores)}):")
        for e in errores[:5]:  # Mostrar solo los primeros 5
            print(f"   - {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Fin de la recogida")
    print("=" * 60)


# =============================================================================
# EJECUCIÓN
# =============================================================================

if __name__ == "__main__":
    ejecutar_recogida()
