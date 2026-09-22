$python = Get-Command python -ErrorAction SilentlyContinue
$pythonCandidates = @(
    if ($python -and ($python.Source -notlike '*WindowsApps*')) { $python.Source }
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe"
) | Where-Object { $_ -and (Test-Path $_) }
$pythonPath = $pythonCandidates | Select-Object -First 1
$gpus = @(Get-CimInstance Win32_VideoController | Select-Object Name, AdapterRAM, DriverVersion)
$system = Get-CimInstance Win32_ComputerSystem
$report = [ordered]@{
    python = $pythonPath
    python_available = [bool]$pythonPath -and ($pythonPath -notlike '*WindowsApps*')
    gpu_count = $gpus.Count
    gpus = $gpus
    total_memory_bytes = $system.TotalPhysicalMemory
    neural_baseline_ready = $false
    reason = 'A real Python interpreter and a supported ML runtime/GPU have not been verified.'
}
$report | ConvertTo-Json -Depth 4
