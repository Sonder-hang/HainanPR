import subprocess, time

# Kill all python processes that might be holding 8001
result = subprocess.run(['powershell', '-Command',
    'Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue | '
    'Select-Object -ExpandProperty OwningProcess | Select-Object -Unique'],
    capture_output=True, text=True)
pids = [int(x) for x in result.stdout.strip().split('\n') if x.strip().isdigit()]
print(f"Processes holding 8001: {pids}")
for pid in pids:
    subprocess.run(['powershell', '-Command', f'Stop-Process -Id {pid} -Force -ErrorAction SilentlyContinue'])
    print(f"  Killed PID {pid}")

time.sleep(3)

# Verify port is free
result = subprocess.run(['powershell', '-Command',
    'Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue | '
    'Select-Object LocalAddress,OwningProcess,State'],
    capture_output=True, text=True)
print(f"Port 8001 status after cleanup:\n{result.stdout}")
if not result.stdout.strip():
    print("Port 8001 is FREE!")
