
# ============================================================
#  SerbiSure API - HTTPie Demo Script
#  Run this file:  .\httpie_demo.ps1
#  Make sure the Django server is running first:
#    venv\Scripts\activate; python manage.py runserver
# ============================================================

$TOKEN = "1a2a6656298b9833447a0cde85ad7ea1d46621cc"

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  1. POST /api/auth/register/  (Register)" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
venv\Scripts\python.exe -m httpie POST http://127.0.0.1:8000/api/auth/register/ `
    email=maria@serbisure.com `
    password=securepass123 `
    full_name="Maria Santos" `
    role=service_worker

Write-Host ""
Write-Host "=========================================" -ForegroundColor Yellow
Write-Host "  2. POST /api/auth/login/  (Login)"      -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Yellow
venv\Scripts\python.exe -m httpie POST http://127.0.0.1:8000/api/auth/login/ `
    email=juan@serbisure.com `
    password=securepass123

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "  3. GET /api/services/  (List Services)" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
venv\Scripts\python.exe -m httpie GET http://127.0.0.1:8000/api/services/

Write-Host ""
Write-Host "=========================================" -ForegroundColor Magenta
Write-Host "  4. GET /api/profile/  (My Profile)"     -ForegroundColor Magenta
Write-Host "=========================================" -ForegroundColor Magenta
venv\Scripts\python.exe -m httpie GET http://127.0.0.1:8000/api/profile/ `
    "Authorization:Token $TOKEN"

Write-Host ""
Write-Host "=========================================" -ForegroundColor Blue
Write-Host "  5. POST /api/bookings/  (Create Booking)" -ForegroundColor Blue
Write-Host "=========================================" -ForegroundColor Blue
venv\Scripts\python.exe -m httpie POST http://127.0.0.1:8000/api/bookings/ `
    "Authorization:Token $TOKEN" `
    service=3 `
    scheduled_date=2026-06-20

Write-Host ""
Write-Host "=========================================" -ForegroundColor White
Write-Host "  6. GET /api/bookings/  (My Bookings)"   -ForegroundColor White
Write-Host "=========================================" -ForegroundColor White
venv\Scripts\python.exe -m httpie GET http://127.0.0.1:8000/api/bookings/ `
    "Authorization:Token $TOKEN"

Write-Host ""
Write-Host "=========================================" -ForegroundColor Red
Write-Host "  7. PATCH /api/bookings/5/ (Update Status)" -ForegroundColor Red
Write-Host "=========================================" -ForegroundColor Red
venv\Scripts\python.exe -m httpie PATCH http://127.0.0.1:8000/api/bookings/5/ `
    "Authorization:Token $TOKEN" `
    status=confirmed

Write-Host ""
Write-Host "===========================================" -ForegroundColor DarkRed
Write-Host "  8. GET /api/bookings/ (No Auth = 401)"   -ForegroundColor DarkRed
Write-Host "===========================================" -ForegroundColor DarkRed
venv\Scripts\python.exe -m httpie GET http://127.0.0.1:8000/api/bookings/

Write-Host ""
Write-Host "=====================================" -ForegroundColor Gray
Write-Host "  All API demo requests completed!"   -ForegroundColor Gray
Write-Host "=====================================" -ForegroundColor Gray
