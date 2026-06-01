$ErrorActionPreference = 'SilentlyContinue'
$proc = Get-CimInstance Win32_Process -Filter "ProcessId = 34596" | Select-Object Name, ProcessId, ExecutablePath
if ($proc) {
    Write-Host "Process found:"
    $proc | Format-List
} else {
    Write-Host "Process 34596 not found"
}
# Also check what python processes are running
$pythonProcs = Get-CimInstance Win32_Process -Filter "Name LIKE '%python%'" | Select-Object Name, ProcessId, ExecutablePath
Write-Host "Python processes:"
$pythonProcs | Format-List
