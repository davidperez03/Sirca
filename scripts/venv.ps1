#!/usr/bin/env pwsh
$ErrorActionPreference = "Stop"

Write-Host "Activando entorno virtual..." -ForegroundColor Green

try {
    # Activar entorno virtual
    if (Test-Path ".\.venv\Scripts\Activate.ps1") {
        Write-Host "Usando ruta de Windows..." -ForegroundColor Yellow
        & .\.venv\Scripts\Activate.ps1
    } elseif (Test-Path ".\.venv\bin\Activate.ps1") {
        Write-Host "Usando ruta alternativa..." -ForegroundColor Yellow
        & .\.venv\bin\Activate.ps1
    } else {
        Write-Host "No se encontró un entorno virtual existente. ¿Deseas crear uno nuevo? (S/N)" -ForegroundColor Yellow
        $respuesta = Read-Host
        if ($respuesta -eq 'S' -or $respuesta -eq 's') {
            Write-Host "Creando nuevo entorno virtual..." -ForegroundColor Cyan
            python -m venv .venv
            if (Test-Path ".\.venv\Scripts\Activate.ps1") {
                & .\.venv\Scripts\Activate.ps1
            } else {
                throw "Error al crear el entorno virtual"
            }
        } else {
            throw "Operación cancelada por el usuario"
        }
    }

    Write-Host "Entorno virtual activado correctamente!" -ForegroundColor Green

    # Actualizar pip y gestionar dependencias
    Write-Host "Actualizando pip..." -ForegroundColor Yellow
    python -m pip install --upgrade pip

    if (Test-Path "requirements.txt") {
        Write-Host "Instalando dependencias desde requirements.txt..." -ForegroundColor Cyan
        pip install -r requirements.txt
    } else {
        Write-Host "No se encontró el archivo requirements.txt" -ForegroundColor Yellow
        Write-Host "¿Deseas instalar las dependencias básicas de Django? (S/N)" -ForegroundColor Yellow
        $respuesta = Read-Host
        if ($respuesta -eq 'S' -or $respuesta -eq 's') {
            Write-Host "Instalando Django..." -ForegroundColor Cyan
            pip install django

            Write-Host "¿Deseas generar un nuevo archivo requirements.txt? (S/N)" -ForegroundColor Yellow
            $generar_req = Read-Host
            if ($generar_req -eq 'S' -or $generar_req -eq 's') {
                pip freeze > requirements.txt
                Write-Host "Archivo requirements.txt generado" -ForegroundColor Green
            }
        } else {
            Write-Host "Instalación de dependencias cancelada" -ForegroundColor Yellow
        }
    }

    Write-Host "Proceso completado exitosamente" -ForegroundColor Green
    Write-Host "Listado de paquetes instalados:" -ForegroundColor Yellow
    pip list
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
