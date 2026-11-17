#!/usr/bin/env bash
# Filtro dei messaggi di commit per la copia pubblica (regola di Davide: niente firme dell'assistente nei repo
# pubblici). Legge il messaggio da stdin, toglie le righe di co-autore dell'assistente e le righe vuote in coda.
# Lo usano sia strumenti/copia_pubblica.sh sia strumenti/copia_pubblica_aggiorna.sh: deve restare identico per
# entrambi, altrimenti gli hash della copia completa e di quella aggiornata non coincidono.
grep -v -i -E '^Co-Authored-By:.*noreply@anthropic\.com' | \
  awk '{ r[NR] = $0 } END { n = NR; while (n > 0 && r[n] ~ /^[[:space:]]*$/) n--; for (i = 1; i <= n; i++) print r[i] }'
