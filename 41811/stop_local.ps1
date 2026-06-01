# ============================================================
# 41811 医疗监管系统 - 停止所有服务（Windows PowerShell）
# ============================================================

$ErrorActionPreference = "SilentlyContinue"

function Stop-Port-Processes {
    param([int]$Port, [string]$Name)
    $procs = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Where-Object { $_.State -eq "Listen" }
    if ($procs) {
        $pids = $procs | Select-Object -ExpandProperty OwningProcess -Unique
        $killed = 0
        foreach ($pid in $pids) {
            $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($proc) {
                Write-Host "[停止] $Name (端口 $Port, PID=$pid)" -ForegroundColor Green
                Stop-Process -Id $pid -Force
                $killed++
            }
        }
        if ($killed -eq 0) {
            Write-Host "[跳过] $Name (端口 $Port) - 进程不存在" -ForegroundColor Yellow
        }
    } else {
        Write-Host "[跳过] $Name (端口 $Port) - 未被占用" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "   41811 医疗监管系统 - 停止所有服务" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""

# 停止顺序：前端最先，后端其次，text2sql 最后
Stop-Port-Processes -Port 5173 -Name "Vue前端"
Stop-Port-Processes -Port 8001 -Name "主后端API"
Stop-Port-Processes -Port 8000 -Name "text2sql服务"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   所有服务已停止" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
