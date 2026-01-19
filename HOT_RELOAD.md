# 🔥 Hot Reload - Guía Completa

## ✅ Sistema de Hot Reload

**Hot reload instantáneo para:**
- ✨ **Estilos globales** (`styles.py`) - ⚡ Instantáneo

**Requiere reinicio (`python dev.py`):**
- 🔄 **Archivos de vistas** (`ui_*.py`) - Reinicio automático en 2-3 segundos

### 🚀 Cómo usar

#### Para cambios en estilos (Recomendado)

```bash
python run.py
```

**Ventajas:**
- ⚡ Cambios instantáneos
- 🎨 Observa `styles.py`
- 🔥 No reinicia la aplicación
- ✅ Estable y sin crashes

#### Para cambios en archivos UI

```bash
python dev.py
```

**Ventajas:**
- 🔄 Reinicia la app completa
- 📦 Soporta cambios en `ui_*.py`
- ⏱️ Tarda 2-3 segundos

---

## 📝 Ejemplos de Uso

### Ejemplo 1: Modificar Estilos Globales (Hot Reload)

1. Ejecuta `python run.py`
2. Abre `src/app/styles.py`
3. Cambia un color en `DARK_STYLES`:
   ```python
   QFrame#sidebar {
       background-color: #ff0000;  # Cambiar a rojo
   }
   ```
4. Guarda (Ctrl+S)
5. ✨ Los cambios aparecen instantáneamente

### Ejemplo 2: Modificar Archivos UI (Reinicio Automático)

1. Ejecuta `python dev.py`
2. Abre `src/app/views/main/ui_mainwindow.py`
3. Modifica cualquier código
4. Guarda (Ctrl+S)
5. 🔄 La app se reinicia automáticamente en 2-3 segundos

---

## 📋 ¿Cuál usar?

| Situación | Comando | Velocidad | Estabilidad |
|-----------|---------|-----------|-------------|
| Cambios de estilos | `python run.py` | ⚡ Instantáneo | ✅ Muy estable |
| Cambios en UI/código | `python dev.py` | 🔄 2-3 segundos | ✅ Estable |

---

## 💡 Recomendación

### ✅ Mejor práctica: Centralizar estilos en `styles.py`

En lugar de poner estilos inline en archivos `ui_*.py`:

```python
# ❌ Evitar: Estilos inline en ui_mainwindow.py
self.sidebar.setStyleSheet(
    "QPushButton { background-color: red; }"
)
```

Ponlos en `styles.py`:

```python
# ✅ Mejor: Estilos centralizados en styles.py
QFrame#sidebar QPushButton {
    background-color: red;
}
```

**Ventajas:**
- ⚡ Hot reload instantáneo
- 📝 Más fácil de mantener
- 🎨 Todos los estilos en un solo lugar

---

## 🎨 Archivos Observados

### Con `python run.py`:
```
src/app/
└── styles.py    ✅ Hot reload instantáneo
```

### Con `python dev.py`:
```
src/
└── **/*.py      ✅ Reinicio automático
```
