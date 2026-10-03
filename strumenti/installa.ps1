# Prepara il repository su un PC nuovo: ambiente Python con le versioni fissate, cartella dei dati in cache,
# cartella delle esecuzioni e collegamento sul Desktop alla finestra di stato.
# Uso, dalla radice del repo:  powershell -NoProfile -ExecutionPolicy Bypass -File strumenti\installa.ps1
$ErrorActionPreference = 'Stop'
$RADICE = Split-Path -Parent $PSScriptRoot
Set-Location $RADICE
$VERSIONE = '3.12.10'

Write-Host '1. Python' -ForegroundColor Cyan
$py = $null
foreach ($cand in @(@('py', '-3.12'), @('python'))) {
    try {
        $v = & $cand[0] $cand[1..9] --version 2>$null
        if ($v -match '3\.12\.') { $py = $cand; break }
    } catch {}
}
if (-not $py) {
    Write-Host "   Python 3.12 non trovato. Installalo con:  winget install Python.Python.3.12 --version $VERSIONE" -ForegroundColor Red
    exit 1
}
$v = & $py[0] $py[1..9] --version
Write-Host "   trovato: $v"
if ($v -notmatch [regex]::Escape($VERSIONE)) {
    Write-Host "   attenzione: il lavoro e' stato fatto con Python $VERSIONE; annotare la differenza nel QUADERNO" -ForegroundColor Yellow
}

Write-Host '2. Ambiente .venv e dipendenze fissate (requirements.txt)' -ForegroundColor Cyan
if (-not (Test-Path '.venv\Scripts\python.exe')) { & $py[0] $py[1..9] -m venv .venv }
& .venv\Scripts\python.exe -m pip install --quiet --upgrade pip
& .venv\Scripts\python.exe -m pip install --quiet -r requirements.txt
& .venv\Scripts\python.exe -c "import numpy, scipy, sklearn; print('   numpy', numpy.__version__, '| scipy', scipy.__version__, '| scikit-learn', sklearn.__version__)"

Write-Host '3. Dati in cache (dati\cache, non sono su GitHub)' -ForegroundColor Cyan
$cache = Join-Path $RADICE 'dati\cache'
if (Test-Path $cache) {
    $n = (Get-ChildItem $cache -Recurse -File | Measure-Object).Count
    $mb = [math]::Round(((Get-ChildItem $cache -Recurse -File | Measure-Object Length -Sum).Sum / 1MB), 0)
    Write-Host "   presenti: $n file, $mb MB"
} else {
    Write-Host '   MANCANO: estrai voynich_cache.zip in dati\cache (vedi le istruzioni del trasloco)' -ForegroundColor Red
}

Write-Host '4. Cartella delle esecuzioni e finestra di stato' -ForegroundColor Cyan
New-Item -ItemType Directory -Force (Join-Path $RADICE 'esecuzioni') | Out-Null
$desktop = [Environment]::GetFolderPath('Desktop')
$bat = Join-Path $desktop 'Stato esperimenti Voynich.bat'
$riga = '@call "' + (Join-Path $RADICE 'strumenti\Stato esperimenti.bat') + '"'
Set-Content -Path $bat -Value $riga -Encoding ASCII
Write-Host "   collegamento sul Desktop: $bat"

Write-Host 'Fatto.' -ForegroundColor Green
