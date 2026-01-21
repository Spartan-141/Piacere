# 🍽️ Sistema de Restaurante - Piacere

Sistema de gestión para restaurantes desarrollado con PySide6 (Qt for Python).

## 📋 Características

- 🔐 Sistema de autenticación de usuarios
- 🪑 Gestión de mesas
- 📋 Gestión de menú
- 📦 Control de inventario
- 💰 Generación de facturas
- 📊 Dashboard con gráficos en tiempo real
- 📈 Reportes y estadísticas avanzadas
- 👥 Administración de usuarios
- 💱 Conversión de tasas de cambio
- 🖨️ Impresión de facturas

---

## 🚀 Instalación para Desarrolladores

### Requisitos Previos

- **Python 3.13** (o 3.10+)
- **pip** (gestor de paquetes de Python)
- **Git** (opcional, para clonar el repositorio)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   git clone <url-del-repositorio>
   cd restaurante_prueba
   ```

2. **Crear entorno virtual** (recomendado)
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

### Dependencias Instaladas

El archivo `requirements.txt` incluye:

```txt
# Framework de interfaz gráfica
PySide6==6.10.0          # Qt for Python

# Utilidades de desarrollo
watchdog==6.0.0          # Hot reload en desarrollo

# Dashboard y visualización de datos
matplotlib>=3.7.0        # Gráficos y visualizaciones
numpy>=1.24.0           # Cálculos numéricos
pillow>=10.0.0          # Procesamiento de imágenes
```

### Ejecutar la Aplicación

**Modo normal:**
```bash
python run.py
```

**Modo desarrollo con hot reload:**
```bash
python dev.py
```

El modo desarrollo reinicia automáticamente la aplicación cuando detecta cambios en el código. Ver [HOT_RELOAD.md](HOT_RELOAD.md) para más detalles.

---

## 📦 Compilar Ejecutable (Para Distribución)

### Requisitos Adicionales

```bash
pip install pyinstaller
```

### Comando de Compilación

Para crear un ejecutable compatible con **Windows 10 y Windows 11**:

```bash
pyinstaller --name="Piacere" --onefile --windowed \
  --add-data="src/app;app" \
  --add-data="src;src" \
  --add-data="data;data" \
  --hidden-import=sqlite3 \
  --hidden-import=logging.handlers \
  --hidden-import=PySide6.QtCore \
  --hidden-import=PySide6.QtGui \
  --hidden-import=PySide6.QtWidgets \
  --hidden-import=PySide6.QtPrintSupport \
  --hidden-import=matplotlib \
  --hidden-import=matplotlib.backends.backend_qt5agg \
  --hidden-import=matplotlib.backends.backend_agg \
  --hidden-import=matplotlib.figure \
  --hidden-import=numpy \
  --hidden-import=numpy.core \
  --hidden-import=numpy.core._multiarray_umath \
  --hidden-import=PIL \
  --hidden-import=PIL.Image \
  --hidden-import=pyparsing \
  --hidden-import=cycler \
  --hidden-import=kiwisolver \
  --hidden-import=contourpy \
  --hidden-import=packaging \
  
powershell
pyinstaller --name "Piacere" --onefile --windowed --clean `
>>   --add-data "src/app;app" --add-data "src;src" --add-data "data;data" `
>>   --hidden-import sqlite3 --hidden-import logging.handlers `
>>   --hidden-import PySide6.QtCore --hidden-import PySide6.QtGui --hidden-import PySide6.QtWidgets `
>>   --hidden-import PySide6.QtPrintSupport --hidden-import matplotlib `
>>   --hidden-import matplotlib.backends.backend_qt5agg --hidden-import matplotlib.backends.backend_agg `
>>   --hidden-import matplotlib.figure --hidden-import numpy --hidden-import numpy.core `
>>   --hidden-import numpy.core._multiarray_umath --hidden-import PIL --hidden-import PIL.Image `
>>   --hidden-import pyparsing --hidden-import cycler --hidden-import kiwisolver `
>>   --hidden-import contourpy --hidden-import packaging `
>>   --collect-data matplotlib --collect-data numpy piacere_main.py

### Resultado

El ejecutable se generará en:
```
dist/Piacere.exe
```

**Tamaño aproximado:** ~74 MB (incluye todas las dependencias)

---

## 🎯 Distribución a Usuarios Finales

### Opción 1: Ejecutable Standalone (Recomendado)

**Ventajas:**
- ✅ No requiere instalación de Python
- ✅ No requiere instalación de dependencias
- ✅ Funciona en Windows 10 y Windows 11
- ✅ Fácil de distribuir

**Archivos a entregar:**
1. `dist\Piacere.exe` - Ejecutable principal
2. `data\` - Carpeta con la base de datos (si no existe, se crea automáticamente)

**Instrucciones para el usuario:**
1. Copiar `Piacere.exe` a cualquier carpeta
2. Ejecutar doble clic en `Piacere.exe`
3. Listo para usar

### Opción 2: Código Fuente

**Solo para desarrolladores o colaboradores técnicos**

**Archivos a entregar:**
- Todo el proyecto completo
- `requirements.txt`
- Este README.md

**Instrucciones:**
Ver sección "Instalación para Desarrolladores" arriba.

---

## 🗂️ Estructura del Proyecto

```
restaurante_prueba/
├── data/                      # Base de datos SQLite
│   └── restaurante.db
├── logs/                      # Archivos de log
├── src/
│   └── app/
│       ├── db/               # Capa de acceso a datos
│       ├── models/           # Modelos de datos
│       ├── services/         # Lógica de negocio
│       ├── views/            # Interfaces de usuario
│       │   ├── dashboard/   # Dashboard con gráficos
│       │   ├── reportes/    # Módulo de reportes
│       │   ├── login/       # Pantalla de login
│       │   └── ...
│       ├── utils/           # Utilidades
│       └── main.py          # Punto de entrada
├── tests/                    # Tests unitarios
├── requirements.txt          # Dependencias del proyecto
├── run.py                   # Script de ejecución normal
├── dev.py                   # Script de desarrollo con hot reload
└── piacere_main.py          # Punto de entrada para PyInstaller
```

---

## 👥 Usuarios por Defecto

Al iniciar la aplicación por primera vez, se crean usuarios de ejemplo:

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| `admin` | `admin` | Administrador |
| `mesero` | `mesero` | Mesero |

**⚠️ Importante:** Cambiar las contraseñas en producción.

---

## 🔧 Solución de Problemas

### El ejecutable no funciona en Windows 10

**Solución:**
1. Verificar que el ejecutable fue compilado con el comando completo (incluye `--collect-data matplotlib`)
2. Instalar [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
3. Verificar que Windows 10 esté actualizado (versión 1809 o superior)

### Error al importar matplotlib

**Solución:**
```bash
pip install --upgrade matplotlib numpy pillow
```

### Base de datos no se crea

**Solución:**
Crear manualmente la carpeta `data/` en el mismo directorio del ejecutable.

---

## 🧪 Testing

Ejecutar tests unitarios:
```bash
pytest
```

Con cobertura:
```bash
pytest --cov=src
```

---

## 📝 Notas de Versión

### Versión Actual

**Características:**
- ✅ Dashboard con gráficos en tiempo real
- ✅ Reportes de ventas y productos
- ✅ Exportación a CSV
- ✅ Compatibilidad Windows 10/11
- ✅ Impresión de facturas

**Dependencias principales:**
- PySide6 6.10.0
- matplotlib 3.10.7
- numpy 2.3.5

---

## 📄 Licencia

[Especificar licencia]

## 🤝 Contribuir

Para contribuir al proyecto:

1. Fork el repositorio
2. Crear una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -am 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear un Pull Request

---

## 📞 Soporte

Para reportar bugs o solicitar características, crear un issue en el repositorio.

