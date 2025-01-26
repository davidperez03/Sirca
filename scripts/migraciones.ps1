$ErrorActionPreference = "Stop"

try {
    Write-Host "Realizando migraciones..." -ForegroundColor Green

    # Crear migraciones
    Write-Host "Creando nuevas migraciones..." -ForegroundColor Cyan
    python manage.py makemigrations

    # Aplicar migraciones
    Write-Host "Aplicando migraciones..." -ForegroundColor Cyan
    python manage.py migrate

    Write-Host "Migraciones completadas exitosamente" -ForegroundColor Green

    # Mostrar migraciones aplicadas
    Write-Host "`nEstado actual de las migraciones:" -ForegroundColor Yellow
    python manage.py showmigrations

} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
