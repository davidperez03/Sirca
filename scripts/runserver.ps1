#!/usr/bin/env pwsh
$ErrorActionPreference = "Stop"

# Obtener la ruta del directorio donde se encuentra este script de PowerShell
$djangoProjectPath = Get-Location

# El puerto del servidor
$serverPort = 8000
$serverUrl = "http://127.0.0.1:$serverPort"

try {
    Write-Host "Iniciando servidor de desarrollo de Django en $serverUrl..." -ForegroundColor Green
    
    # Navegar a la carpeta del proyecto
    Set-Location -Path $djangoProjectPath

    # Iniciar el servidor de desarrollo de Django sin mostrar la ventana de la terminal
    Start-Process "python" -ArgumentList "manage.py runserver $serverPort" 
    
    # Esperar un momento para asegurar que el servidor haya iniciado
    Start-Sleep -Seconds 2

    # Verificar si el servidor está corriendo antes de abrir el navegador usando Test-NetConnection
    $response = Test-NetConnection -ComputerName "127.0.0.1" -Port $serverPort
    if ($response.TcpTestSucceeded) {
        # Abrir el navegador en la URL de Django
        Start-Process $serverUrl
        Write-Host "Servidor iniciado correctamente. Accede a $serverUrl en tu navegador." -ForegroundColor Green
    } else {
        Write-Host "No se pudo conectar al servidor en $serverUrl. Asegúrate de que el servidor esté ejecutándose." -ForegroundColor Red
    }

} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
