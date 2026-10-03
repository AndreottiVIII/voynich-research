#!/usr/bin/env bash
# Esegue in sequenza gli esperimenti dati come argomenti (formato: [VAR=val,...:]eNNN) e scrive una riga di stato per
# ciascuno in esecuzioni/stato_code.txt; l'uscita di ogni esperimento va in esecuzioni/eNNN.log.
# Con --dopo eNNN come primo argomento dopo il nome, aspetta che nello stato compaia "FINE eNNN".
# Uso, dalla radice del repo, staccato dalla sessione:
#   nohup bash strumenti/coda.sh NOME e243 e257 "RIPARTENZE=2,PROCESSI=2:e212b" > /dev/null 2>&1 &
#   nohup bash strumenti/coda.sh NOME --dopo e243b e276 > /dev/null 2>&1 &
RADICE=$(cd "$(dirname "$0")/.." && pwd)
E=$RADICE/esecuzioni
mkdir -p "$E"
STATO=$E/stato_code.txt
cd "$RADICE" || exit 1
export PYTHONIOENCODING=utf-8
PY=.venv/Scripts/python
[ -x "$PY" ] || [ -x "$PY.exe" ] || PY=.venv/bin/python
nome=$1; shift
if [ "$1" = "--dopo" ]; then
  attesa=$2; shift 2
  echo "$(date +%H:%M) [$nome] in attesa della fine di $attesa" >> "$STATO"
  while ! grep -q "FINE $attesa " "$STATO" 2>/dev/null; do sleep 60; done
fi
for voce in "$@"; do
  vars=""; e=$voce
  if [[ "$voce" == *:* ]]; then vars=${voce%%:*}; e=${voce#*:}; fi
  echo "$(date +%H:%M) [$nome] avvio $e" >> "$STATO"
  ( IFS=','; for kv in $vars; do export "$kv"; done; $PY esegui.py "$e" > "$E/$e.log" 2>&1 ); rc=$?
  echo "$(date +%H:%M) [$nome] FINE $e uscita $rc" >> "$STATO"
done
echo "$(date +%H:%M) [$nome] coda finita" >> "$STATO"
