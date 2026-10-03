# Stato degli esperimenti Voynich, aggiornato ogni minuto (Ctrl-C per chiudere; gli esperimenti continuano).
# Legge esecuzioni\stato_code.txt (scritto da strumenti\coda.sh), esecuzioni\in_coda.txt (righe "eNNN|descrizione|motivo")
# ed esecuzioni\in_preparazione.txt (lavoro di Claude non ancora in coda: progetti, preregistrazioni, codice).
$RADICE = Split-Path -Parent $PSScriptRoot
$E = Join-Path $RADICE 'esecuzioni'
$CARTELLALOG = Join-Path $RADICE 'risultati\provenienza'
$STATO = Join-Path $E 'stato_code.txt'
$CODA = Join-Path $E 'in_coda.txt'
$PREP = Join-Path $E 'in_preparazione.txt'   # righe "voce|descrizione|a che punto", tenute aggiornate da Claude
while ($true) {
    $procs = Get-CimInstance Win32_Process -Filter "Name like 'python%'"
    $perId = @{}
    foreach ($p in $procs) { $perId[[int]$p.ProcessId] = $p }
    $esperimenti = @{}
    foreach ($p in $procs) {
        $nome = $null
        if ($p.CommandLine -match 'esperimenti[\\/](e\d+[a-z]?)_') { $nome = $Matches[1] }
        elseif ($p.CommandLine -match 'multiprocessing' -and $perId.ContainsKey([int]$p.ParentProcessId)) {
            $par = $perId[[int]$p.ParentProcessId].CommandLine
            if ($par -match 'esperimenti[\\/](e\d+[a-z]?)_') { $nome = $Matches[1] }
        }
        if ($nome) {
            $cpu = 0
            try { $cpu = (Get-Process -Id $p.ProcessId -ErrorAction Stop).CPU } catch {}
            if (-not $esperimenti.ContainsKey($nome)) { $esperimenti[$nome] = 0 }
            $esperimenti[$nome] += $cpu
        }
    }
    Clear-Host
    Write-Host ('Esperimenti Voynich - aggiornato alle ' + (Get-Date -Format 'HH:mm:ss')) -ForegroundColor Cyan
    Write-Host ''
    Write-Host ('IN ESECUZIONE (' + $esperimenti.Count + ')') -ForegroundColor Green
    foreach ($e in ($esperimenti.Keys | Sort-Object)) {
        $ultima = ''
        $log = Join-Path $CARTELLALOG ($e + '.log')
        if (Test-Path $log) {
            $ultima = (Get-Content $log -Tail 1 -Encoding UTF8)
            if ($ultima -and $ultima.Length -gt 90) { $ultima = $ultima.Substring(0, 90) + '...' }
        }
        Write-Host ('  {0,-6} CPU {1,7:N0} s   {2}' -f $e, $esperimenti[$e], $ultima)
    }
    Write-Host ''
    $avviati = @()
    if (Test-Path $STATO) {
        foreach ($riga in (Get-Content $STATO)) { if ($riga -match 'avvio (e\w+)') { $avviati += $Matches[1] } }
    }
    $attesa = @()
    if (Test-Path $CODA) {
        foreach ($riga in (Get-Content $CODA -Encoding UTF8)) {
            $parti = $riga.Split('|')
            if ($parti.Count -ge 3 -and -not ($avviati -contains $parti[0]) -and -not $esperimenti.ContainsKey($parti[0])) { $attesa += $parti }
        }
    }
    Write-Host ('IN CODA (' + ($attesa.Count / 3) + ')') -ForegroundColor Magenta
    for ($i = 0; $i -lt $attesa.Count; $i += 3) {
        Write-Host ('  {0,-6} {1,-48} {2}' -f $attesa[$i], $attesa[$i + 1], $attesa[$i + 2])
    }
    Write-Host ''
    if (Test-Path $PREP) {
        $prep = @(Get-Content $PREP -Encoding UTF8 | Where-Object { $_ -match '\|' })
        Write-Host ('IN PREPARAZIONE DA CLAUDE (' + $prep.Count + ')') -ForegroundColor Blue
        foreach ($riga in $prep) {
            $parti = $riga.Split('|')
            Write-Host ('  {0,-9} {1,-52} {2}' -f $parti[0], $parti[1], $parti[2])
        }
        Write-Host ''
    }
    Write-Host 'ULTIMI EVENTI DELLE CODE' -ForegroundColor Yellow
    if (Test-Path $STATO) {
        Get-Content $STATO -Tail 12 | ForEach-Object { Write-Host ('  ' + $_) }
    }
    Write-Host ''
    Write-Host 'Si aggiorna ogni 60 secondi. Ctrl-C per chiudere (gli esperimenti continuano comunque).' -ForegroundColor DarkGray
    Start-Sleep -Seconds 60
}
