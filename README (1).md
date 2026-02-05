# 🚄 Renfe Price Tracker

Herramienta para rastrear automáticamente los precios de trenes Renfe y descubrir el mejor momento para comprar billetes.

## 📊 ¿Qué hace?

- Recoge precios de trenes **dos veces al día** (8:00 y 20:00)
- Guarda un histórico para analizar tendencias
- Te ayuda a saber **cuántos días antes** conviene comprar

## 🚂 Rutas configuradas

| Ruta | Dirección | Uso típico |
|------|-----------|------------|
| BCN → VLL | Barcelona → Valladolid | Ida (viernes) |
| VLL → BCN | Valladolid → Barcelona | Vuelta (domingo) |

---

## 🚀 Cómo configurarlo (paso a paso)

### Paso 1: Crear cuenta en GitHub

1. Ve a [github.com](https://github.com)
2. Click en **"Sign up"** (arriba a la derecha)
3. Sigue los pasos (email, contraseña, nombre de usuario)
4. Verifica tu email

### Paso 2: Crear un repositorio nuevo

1. Una vez dentro de GitHub, click en el **"+"** (arriba a la derecha)
2. Selecciona **"New repository"**
3. Configura:
   - **Repository name:** `renfe-price-tracker` (o el nombre que quieras)
   - **Description:** `Rastreador de precios de trenes Renfe`
   - ✅ Marca **"Public"** (necesario para GitHub Actions gratis)
   - ✅ Marca **"Add a README file"**
4. Click en **"Create repository"**

### Paso 3: Subir los archivos

#### Opción A: Desde la web (más fácil)

1. En tu repositorio, click en **"Add file"** → **"Upload files"**
2. Arrastra estos archivos:
   - `recoger_precios.py`
   - `analizar_precios.py`
3. Click en **"Commit changes"**

4. Ahora crea la carpeta para el workflow:
   - Click en **"Add file"** → **"Create new file"**
   - En el nombre escribe: `.github/workflows/recoger_precios.yml`
   - Copia el contenido del archivo `recoger_precios.yml`
   - Click en **"Commit changes"**

5. Crea la carpeta de datos:
   - Click en **"Add file"** → **"Create new file"**
   - En el nombre escribe: `data/.gitkeep`
   - Deja el contenido vacío
   - Click en **"Commit changes"**

#### Opción B: Usando Git (si ya lo tienes instalado)

```bash
git clone https://github.com/TU_USUARIO/renfe-price-tracker.git
cd renfe-price-tracker
# Copia los archivos aquí
git add .
git commit -m "Setup inicial"
git push
```

### Paso 4: Verificar que funciona

1. Ve a la pestaña **"Actions"** en tu repositorio
2. Deberías ver el workflow "🚄 Recoger precios Renfe"
3. Click en él → **"Run workflow"** → **"Run workflow"** (botón verde)
4. Espera unos minutos y verifica que aparece ✅ verde

### Paso 5: ¡Listo! 🎉

El script se ejecutará automáticamente dos veces al día. Los datos se guardarán en `data/precios_historico.csv`.

---

## 📈 Cómo analizar los datos

### Opción 1: Google Colab (recomendado)

1. Ve a [colab.research.google.com](https://colab.research.google.com)
2. Crea un notebook nuevo
3. Ejecuta:

```python
# Descargar los datos desde tu repositorio
!wget https://raw.githubusercontent.com/TU_USUARIO/renfe-price-tracker/main/data/precios_historico.csv -O precios.csv

# Cargar y analizar
import pandas as pd
df = pd.read_csv('precios.csv')
print(f"Total registros: {len(df)}")
df.head()
```

4. Copia el contenido de `analizar_precios.py` en celdas para ejecutar los análisis

### Opción 2: Localmente

```bash
git pull  # Descargar últimos datos
python analizar_precios.py
```

---

## 📁 Estructura del proyecto

```
renfe-price-tracker/
├── .github/
│   └── workflows/
│       └── recoger_precios.yml    # ← Automatización
├── data/
│   └── precios_historico.csv      # ← Datos acumulados
├── recoger_precios.py             # ← Script de recogida
├── analizar_precios.py            # ← Script de análisis
└── README.md                      # ← Este archivo
```

---

## ⚙️ Personalización

### Cambiar las rutas

Edita `recoger_precios.py`, sección `RUTAS`:

```python
RUTAS = [
    {"origen": "Barcelona", "destino": "Valladolid", "nombre": "BCN_VLL"},
    {"origen": "Valladolid", "destino": "Barcelona", "nombre": "VLL_BCN"},
    # Añade más rutas aquí:
    {"origen": "Madrid", "destino": "Barcelona", "nombre": "MAD_BCN"},
]
```

### Cambiar la frecuencia de recogida

Edita `.github/workflows/recoger_precios.yml`, sección `schedule`:

```yaml
schedule:
  - cron: '0 7 * * *'   # 8:00 España
  - cron: '0 19 * * *'  # 20:00 España
  # Formato: minuto hora día mes día_semana
  # Ejemplos:
  # '0 12 * * *'     → cada día a las 12:00 UTC
  # '0 */6 * * *'    → cada 6 horas
  # '0 8 * * 1-5'    → lunes a viernes a las 8:00 UTC
```

### Cambiar semanas a consultar

Edita `recoger_precios.py`:

```python
SEMANAS_ADELANTE = 8  # Cambia a 10, 12, etc.
```

---

## ❓ Problemas comunes

### "Actions" no aparece o está deshabilitado

1. Ve a **Settings** → **Actions** → **General**
2. Selecciona **"Allow all actions"**
3. Guarda

### El workflow falla

1. Ve a **Actions** → Click en el workflow fallido
2. Mira los logs para ver el error
3. Los errores más comunes:
   - `ModuleNotFoundError`: Falta alguna dependencia
   - `Permission denied`: El repo debe ser público

### No se guardan los datos

Verifica que el workflow tiene permisos de escritura:
- En el archivo `.yml` debe estar `permissions: contents: write`

---

## 📊 Ejemplo de análisis tras 2 meses

Una vez tengas datos de 6-8 semanas, podrás ver patrones como:

```
📅 VIERNES (BCN → VLL)
   Mejor momento para comprar: 15-20 días antes
   Precio medio: 58€
   Precio mínimo conseguido: 37€ (ALVIA 09:05)

📅 DOMINGO (VLL → BCN)  
   Mejor momento para comprar: 10-15 días antes
   Precio medio: 52€
   Precio mínimo conseguido: 35€ (AVE 18:00)
```

---

## 📝 Licencia

MIT - Usa este código como quieras.

---

**¿Preguntas?** Abre un Issue en el repositorio.
