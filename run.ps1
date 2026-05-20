$ErrorActionPreference = 'Stop'

$VenvDir = '.venv'

if (-not (Test-Path $VenvDir)) {
    Write-Host "Creating virtual environment..."
    python -m venv $VenvDir
}

& "$VenvDir\Scripts\Activate.ps1"
pip install --quiet -r requirements.txt

if ($args[0] -eq '--web') {
    python web.py
} else {
    python -m mastocloud.main @args
}

deactivate
