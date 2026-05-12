# ============================================================
# 41811 医疗监管系统 - 本地启动脚本（Windows PowerShell）
#
# 使用方式:
#   右键 -> 使用 PowerShell 运行
#   或在 PowerShell 中: .\start_local.ps1
#
# 停止: .\stop_local.ps1
# ============================================================

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

# 颜色
function Write-Step { param($msg) Write-Host "[启动] $msg" -ForegroundColor Cyan }
function Write-Ok   { param($msg) Write-Host "[OK]    $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "[警告] $msg" -ForegroundColor Yellow }
function Write-Err  { param($msg) Write-Host "[错误] $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "       $msg" }

# 端口占用检测
function Test-Port {
    param([int]$Port)
    $conn = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    return $null -ne $conn
}

# 停止指定端口的进程
function Stop-Port {
    param([int]$Port, [string]$Name)
    $procs = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Where-Object { $_.State -eq "Listen" }
    if ($procs) {
        $pids = $procs | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($pid in $pids) {
            $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($proc) {
                Write-Warn "停止旧进程: $($proc.ProcessName) (PID=$pid) 端口 $Port"
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            }
        }
        Start-Sleep -Milliseconds 500
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "   41811 医疗监管系统 - 本地启动" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""

# ---- 检查端口占用 ----
$ports = @{ 8000 = "text2sql"; 8001 = "主后端API"; 5173 = "Vue前端" }
foreach ($port in $ports.Keys) {
    if (Test-Port $port) {
        Write-Warn "端口 $port ($($ports[$port])) 已被占用，将先停止旧进程..."
        Stop-Port $port $ports[$port]
    }
}

# ---- 1. text2sql 服务 (端口 8000) ----
Write-Step "启动 text2sql 服务 (端口 8000)..."
$text2sqlDir = Join-Path $ProjectRoot "backend_fastapi\Hainan_SQL-main\text2sql_app"
if (-not (Test-Path $text2sqlDir)) {
    Write-Err "text2sql 目录不存在: $text2sqlDir"
    exit 1
}
$pythonExe = "python"
$text2sqlProc = Start-Process $pythonExe -ArgumentList "run.py" -WorkingDirectory $text2sqlDir -NoNewWindow -PassThru -RedirectStandardOutput "$env:TEMP\text2sql_stdout.log" -RedirectStandardError "$env:TEMP\text2sql_stderr.log"
Write-Ok "text2sql 已启动 (PID=$($text2sqlProc.Id))"
Write-Info "日志: $env:TEMP\text2sql_stdout.log"

# ---- 2. 主后端 API (端口 8001) ----
Write-Step "等待 text2sql 服务就绪..."
Start-Sleep -Seconds 3

Write-Step "启动主后端 API (端口 8001)..."
$backendDir = Join-Path $ProjectRoot "backend_fastapi"
if (-not (Test-Path $backendDir)) {
    Write-Err "backend_fastapi 目录不存在: $backendDir"
    exit 1
}
$backendProc = Start-Process $pythonExe -ArgumentList "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8001", "--app-dir", $backendDir -NoNewWindow -PassThru -RedirectStandardOutput "$env:TEMP\backend_stdout.log" -RedirectStandardError "$env:TEMP\backend_stderr.log"
Write-Ok "主后端 API 已启动 (PID=$($backendProc.Id))"
Write-Info "日志: $env:TEMP\backend_stdout.log"

# ---- 3. Vue 前端 (端口 5173) ----
Write-Step "启动 Vue 前端 (端口 5173)..."
$frontendDir = Join-Path $ProjectRoot "my-vue-app"
if (-not (Test-Path $frontendDir)) {
    Write-Err "my-vue-app 目录不存在: $frontendDir"
    exit 1
}
$npmExe = "npm.cmd"
$frontendProc = Start-Process $npmExe -ArgumentList "run", "dev" -WorkingDirectory $frontendDir -NoNewWindow -PassThru -RedirectStandardOutput "$env:TEMP\frontend_stdout.log" -RedirectStandardError "$env:TEMP\frontend_stderr.log"
Write-Ok "Vue 前端已启动 (PID=$($frontendProc.Id))"
Write-Info "日志: $env:TEMP\frontend_stdout.log"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   所有服务已启动！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  text2sql:  http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "  主后端API: http://127.0.0.1:8001" -ForegroundColor Yellow
Write-Host "  Vue前端:   http://localhost:5173" -ForegroundColor Yellow
Write-Host ""
Write-Host "  停止所有服务: .\stop_local.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "  [注意] text2sql 服务依赖远程 MySQL 和远程 LLM。" -ForegroundColor Yellow
Write-Host "         请确保以下地址可达:" -ForegroundColor Yellow
Write-Host "           MySQL: 127.0.0.1:3306 (或修改 config.py)" -ForegroundColor Yellow
Write-Host "           LLM:   http://10.114.255.26:9233/v1" -ForegroundColor Yellow
Write-Host ""

# 等待前台
Write-Host "按 Ctrl+C 停止所有服务，或关闭此窗口..." -ForegroundColor DarkGray
try {
    while ($true) { Start-Sleep -Seconds 10 }
} finally {
    Write-Host ""
    Write-Host "正在停止所有服务..."
    @($text2sqlProc, $backendProc, $frontendProc) | ForEach-Object {
        if ($_ -and -not $_.HasExited) {
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
    }
    Write-Host "已停止。" -ForegroundColor Green
}
