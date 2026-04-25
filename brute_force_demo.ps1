# ============================================================
# SerbiSure - Brute Force Attack Simulation Script
# For security presentation / video demo purposes
# ============================================================

$url     = "http://127.0.0.1:8000/api/v1/auth/login/"
$headers = @{ "Content-Type" = "application/json" }

$passwords = @(
    "wrong1", "wrong2", "wrong3", "wrong4", "wrong5",
    "letmein", "password", "123456", "admin", "qwerty",
    "iloveyou", "123456789", "abc123", "111111", "1234567",
    "dragon", "master", "monkey", "sunshine", "princess"
)

Write-Host ""
Write-Host "======================================================" -ForegroundColor Red
Write-Host "   BRUTE FORCE ATTACK SIMULATION - SerbiSure API     " -ForegroundColor Red
Write-Host "======================================================" -ForegroundColor Red
Write-Host "Target:  $url" -ForegroundColor Cyan
Write-Host "Account: homeowner@test.com" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting attack simulation..." -ForegroundColor Yellow
Write-Host ""

$blocked = $false

for ($i = 0; $i -lt $passwords.Count; $i++) {
    $pw      = $passwords[$i]
    $attempt = $i + 1
    $body    = '{"email":"homeowner@test.com","password":"' + $pw + '"}'

    try {
        $response = Invoke-RestMethod -Uri $url -Method POST -Headers $headers -Body $body -ErrorAction Stop
        Write-Host "  Attempt $attempt | Password: '$pw' | [SUCCESS] ACCOUNT COMPROMISED!" -ForegroundColor Green
        $blocked = $false
        break
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__

        if ($statusCode -eq 429) {
            Write-Host "  Attempt $attempt | Password: '$pw' | [429] TOO MANY REQUESTS - RATE LIMITED!" -ForegroundColor Red
            Write-Host ""
            Write-Host "======================================================" -ForegroundColor Green
            Write-Host "  SERVER BLOCKED THE ATTACK! Throttle limit reached.  " -ForegroundColor Green
            Write-Host "======================================================" -ForegroundColor Green
            $blocked = $true
            break
        }
        elseif ($statusCode -eq 401) {
            Write-Host "  Attempt $attempt | Password: '$pw' | [401] Unauthorized - wrong password" -ForegroundColor Yellow
        }
        else {
            Write-Host "  Attempt $attempt | Password: '$pw' | [HTTP $statusCode]" -ForegroundColor Gray
        }
    }

    Start-Sleep -Milliseconds 300
}

Write-Host ""
if ($blocked) {
    Write-Host "RESULT: Brute force attack was BLOCKED by rate limiting." -ForegroundColor Green
    Write-Host "        The attacker cannot continue. Server is protected." -ForegroundColor Green
}
else {
    Write-Host "RESULT: All attempts exhausted. Account not compromised." -ForegroundColor Cyan
    Write-Host "        NOTE: Rate limit kicks in after 10 requests/minute." -ForegroundColor Yellow
}
Write-Host ""
Write-Host "Check the Django server terminal to see all login attempts logged." -ForegroundColor Cyan
