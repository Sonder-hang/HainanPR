$ErrorActionPreference = 'SilentlyContinue'
$proc = Get-CimInstance Win32_Process -Filter "ProcessId = 43748" | Select-Object Name, ProcessId, ExecutablePath
if ($proc) {
    Write-Host "PID 43748 found:"
    $proc | Format-List
} else {
    Write-Host "PID 43748 not found"
}
$proc2 = Get-CimInstance Win32_Process -Filter "ProcessId = 28500" | Select-Object Name, ProcessId, ExecutablePath
if ($proc2) {
    Write-Host "PID 28500 found:"
    $proc2 | Format-List
} else {
    Write-Host "PID 28500 not found"
}
