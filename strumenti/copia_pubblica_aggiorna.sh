#!/usr/bin/env bash
# Aggiorna la copia pubblica (fatta da strumenti/copia_pubblica.sh) con i commit nuovi del repo di lavoro, senza
# rifarla da capo. A ogni commit nuovo, in ordine, applica lo stesso trattamento della copia completa:
#   - stesse esclusioni (ESCLUSI) e stessa email anonima (EMAIL_PUBBLICA), lette da copia_pubblica.sh;
#   - stessi nomi, date e messaggio del commit originale.
# Gli hash vengono quindi uguali a quelli che darebbe la copia completa (si può verificare rifacendola da capo).
# Funziona solo con storia lineare: i commit nuovi non devono essere merge.
#
# Uso, dalla radice del repo di lavoro:
#   bash strumenti/copia_pubblica_aggiorna.sh [cartella della copia]
# poi, nella copia: git push (il remote è github.com/AndreottiVIII/voynich-research)
set -euo pipefail
RADICE=$(cd "$(dirname "$0")/.." && pwd)
DEST=${1:-$RADICE/../voynich-pubblico}
eval "$(grep -E "^(EMAIL_PUBBLICA|ESCLUSI)=" "$RADICE/strumenti/copia_pubblica.sh")"
MAPPA=${MAPPA:-$RADICE/esecuzioni/mappa_commit_pubblici.txt}
cd "$DEST"

ultimo_privato=$(tail -n 1 "$MAPPA" | cut -d' ' -f1)
ultimo_pubblico=$(tail -n 1 "$MAPPA" | cut -d' ' -f2)
test "$(git rev-parse main)" = "$ultimo_pubblico" || { echo 'ERRORE: la copia non è all ultimo commit della mappa'; exit 1; }

git fetch -q --no-tags "$RADICE" main:refs/privato/main
nuovi=$(git rev-list --reverse refs/privato/main "^$ultimo_privato")
INDICE=$(mktemp)
trap 'rm -f "$INDICE"' EXIT
n=0
for c in $nuovi; do
  genitori=$(git rev-list --parents -n 1 "$c" | cut -d' ' -f2-)
  test "$(echo "$genitori" | wc -w)" = 1 || { echo "ERRORE: $c ha più genitori"; exit 1; }
  p_pubblico=$(grep "^$genitori " "$MAPPA" | cut -d' ' -f2)
  test -n "$p_pubblico" || { echo "ERRORE: genitore di $c non nella mappa"; exit 1; }
  rm -f "$INDICE"
  GIT_INDEX_FILE=$INDICE git read-tree "$c"
  GIT_INDEX_FILE=$INDICE git rm -r -q --cached --ignore-unmatch $ESCLUSI
  albero=$(GIT_INDEX_FILE=$INDICE git write-tree)
  testa=$(git cat-file commit "$c" | sed -n '1,/^$/p')
  autore=$(echo "$testa" | sed -n 's/^author //p')
  committente=$(echo "$testa" | sed -n 's/^committer //p')
  nuovo=$(git cat-file commit "$c" | sed -e '1,/^$/d' | \
    GIT_AUTHOR_NAME="$(echo "$autore" | sed 's/ <.*//')" GIT_AUTHOR_EMAIL="$EMAIL_PUBBLICA" \
    GIT_AUTHOR_DATE="@$(echo "$autore" | sed 's/.*> //')" \
    GIT_COMMITTER_NAME="$(echo "$committente" | sed 's/ <.*//')" GIT_COMMITTER_EMAIL="$EMAIL_PUBBLICA" \
    GIT_COMMITTER_DATE="@$(echo "$committente" | sed 's/.*> //')" \
    git commit-tree "$albero" -p "$p_pubblico")
  echo "$c $nuovo" >> "$MAPPA"
  git update-ref refs/heads/main "$nuovo"
  n=$((n + 1))
done
git update-ref -d refs/privato/main
rm -f .git/FETCH_HEAD
git reflog expire --expire=now --all
git gc -q --prune=now
git reset -q --hard main

# controlli, come nella copia completa
test -z "$(git for-each-ref --format='%(refname)' | grep -v -x -E 'refs/heads/main|refs/remotes/origin/(main|HEAD)' || true)" || { echo 'ERRORE: riferimenti oltre main'; exit 1; }
test -z "$(git log --all --format='%ae%n%ce' | grep -v -x "$EMAIL_PUBBLICA" || true)" || { echo 'ERRORE: email non anonime'; exit 1; }
test -z "$(git rev-list --objects --all | grep -E '(note_revisore_v1_(EN|IT)\.md|VERIFICA_NOTE_REVISORE\.md|white_paper/(zenodo|linkedin))' || true)" || { echo 'ERRORE: file esclusi presenti'; exit 1; }
test "$(git fsck --unreachable --no-reflogs 2>/dev/null | wc -l)" = 0 || { echo 'ERRORE: oggetti della storia privata rimasti'; exit 1; }
test -z "$(git cat-file --batch-all-objects --batch-check='%(objecttype) %(objectname)' | awk '$1 == "commit" {print $2}' | \
  xargs -r -n 200 git show -s --format='%ae%n%ce' | grep -v -x "$EMAIL_PUBBLICA" || true)" || { echo 'ERRORE: commit con email non anonime nel deposito'; exit 1; }
echo "commit aggiunti: $n; commit nella copia: $(git rev-list --count main); mappa: $(wc -l < "$MAPPA") righe"
