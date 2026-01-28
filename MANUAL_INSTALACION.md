# 📖 Manual de Instalación - Piacere

Este documento proporciona las instrucciones necesarias para instalar y configurar el sistema **Piacere** en una computadora de usuario final.

---

## 💻 Requisitos del Sistema

Para un funcionamiento óptimo, se recomienda:

*   **Sistema Operativo:** Windows 10 o Windows 11 (64 bits).
*   **Memoria RAM:** 4 GB o superior.
*   **Espacio en Disco:** 200 MB libres.
*   **Resolución de Pantalla:** 1280x720 o superior.

---

## 🚀 Pasos para la Instalación

Dado que el sistema se entrega como un archivo ejecutable (.exe), no requiere de un proceso de instalación complejo. Siga estos pasos:

### 1. Preparación de la Carpeta
Se recomienda crear una carpeta específica para el sistema en una ubicación accesible, por ejemplo: `C:\Piacere`.

### 2. Copia de Archivos
Copie el archivo `Piacere.exe` dentro de la carpeta que acaba de crear.

### 3. Ejecución por primera vez
Haga doble clic en `Piacere.exe`. 

> [!NOTE]
> Al ejecutar por primera vez, el sistema creará automáticamente una carpeta llamada `data` y un archivo `restaurante.db` dentro de ella. Esta es la base de datos donde se guardará toda su información. **No elimine esta carpeta.**

---

## 🔐 Acceso al Sistema

Una vez abierta la aplicación, utilice las siguientes credenciales por defecto para ingresar:

| Usuario | Contraseña | Rol |
| :--- | :--- | :--- |
| `admin` | `admin` | Administrador (Acceso total) |

> [!IMPORTANT]
> Se recomienda cambiar estas contraseñas una vez haya ingresado al sistema a través del módulo de **Usuarios** o **Mi Perfil**.

---

## 🛠️ Solución de Problemas Comunes

### El programa no abre o falta un archivo .dll
Es posible que su sistema Windows necesite los componentes de Visual C++. Puede descargarlos e instalarlos desde el sitio oficial de Microsoft:
[Descargar Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)

### Advertencia de SmartScreen de Windows
Al ser un archivo nuevo, Windows puede mostrar una advertencia azul diciendo "Windows protegió su PC".
1. Haga clic en **"Más información"**.
2. Haga clic en **"Ejecutar de todas formas"**.

---

## 💾 Respaldo de Datos (Backup)

Para proteger su información, se recomienda realizar copias de seguridad periódicas:
1. Sierre el programa.
2. Copie la carpeta `data` (la que contiene el archivo `restaurante.db`) a un disco externo o servicio en la nube (Google Drive, OneDrive, etc.).

---

## 📞 Soporte Técnico

Si encuentra algún inconveniente técnico o necesita asistencia adicional, por favor contacte al administrador del sistema o al desarrollador.
