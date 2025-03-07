# Creación de Entorno Virtual en Python

Para gestionar las dependencias del proyecto de manera aislada, se recomienda el uso de un entorno virtual. A continuación, se detallan los pasos para su creación y activación.

## 1️⃣ Instalar virtualenv (Opcional)

Si deseas usar `virtualenv` en lugar del módulo `venv` de Python, instala `virtualenv` con:

```sh
pip install virtualenv
```

## 2️⃣ Crear el Entorno Virtual

Usando virtualenv:

```sh
virtualenv .venv
```

O usando venv (recomendado, ya incluido en Python):

```sh
python -m venv .venv
```

## 3️⃣ Activar el Entorno virtual

En Windows (CMD o PowerShell)

```sh
.venv\Scripts\activate

```

En PowerShell puede ser necesario usar:

```sh
.venv\Scripts\Activate.ps1
```

En Linux o MacOS

```sh
source .venv/bin/activate
```

## 4️⃣ Instalar Dependencias

Instala las dependencias con:

```sh
pip install -r requerimientos.txt
```

## 5️⃣ Desactivar Entorno Virtual

Para desactivar el entorno virtual, usa:

```sh
deactivate
```

## ✅ Recomendación para este proyecto

Se recomienda el uso de `venv` en combinación con `.venv` como nombre del entorno virtual, debido a que:

- `venv` es el módulo estándar de Python, por lo que no requiere instalaciones adicionales.
- `.venv` ayuda a ocultar el directorio en sistemas Unix (Linux/macOS), reduciendo el ruido en el explorador de archivos y en herramientas como Git.
- Mejora la compatibilidad con IDEs como VS Code, que detectan automáticamente `.venv`.

Si prefieres otro nombre para el entorno virtual, asegúrate de actualizar la configuración en tu editor de código y en el `.gitignore` si es necesario.
