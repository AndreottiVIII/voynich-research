#!/usr/bin/env bash
# Prepara la copia pubblica del repository (decisione di Davide del 9/10/2026: il repo di lavoro resta privato, si
# pubblica una copia).
#
# Che cosa cambia nella copia, per tutta la storia del ramo main:
#   - autore e committente di ogni commit hanno l'indirizzo anonimo di GitHub (EMAIL_PUBBLICA); nomi e date restano
#     quelli originali, quindi lo script è deterministico: rieseguito più avanti dà gli stessi hash per i commit già
#     pubblicati e la copia si aggiorna senza riscrivere la storia;
#   - le note del revisore esterno e la nostra verifica punto per punto (ESCLUSI) non ci sono, in nessun commit
#     (decisione di Davide del 9/10/2026);
#   - i materiali di pubblicazione (white_paper/zenodo, white_paper/linkedin) non ci sono (decisione di Davide, 9/10).
# Gli hash dei commit cambiano: i file di provenienza (risultati/provenienza/*.json) citano gli hash del repo di lavoro.
# Lo script scrive la corrispondenza vecchio -> nuovo in MAPPA (una riga "hash_privato hash_pubblico" per commit);
# si conserva nel repo di lavoro come risultati/provenienza/MAPPA_COMMIT_PUBBLICI.txt, così arriva anche nella copia.
#
# Uso, dalla radice del repo (staccato, ci mette una ventina di minuti):
#   nohup bash strumenti/copia_pubblica.sh > esecuzioni/copia_pubblica.log 2>&1 &
# La copia finisce in ../voynich-pubblico (o nella cartella data come primo argomento), senza remote: la pubblicazione
# su GitHub la fa Davide.
set -euo pipefail
RADICE=$(cd "$(dirname "$0")/.." && pwd)
DEST=${1:-$RADICE/../voynich-pubblico}
EMAIL_PUBBLICA='AndreottiVIII@users.noreply.github.com'
ESCLUSI='white_paper/revisione/note_revisore_v1_EN.md white_paper/revisione/note_revisore_v1_IT.md white_paper/revisione/VERIFICA_NOTE_REVISORE.md white_paper/zenodo white_paper/linkedin'
MAPPA=$RADICE/esecuzioni/mappa_commit_pubblici.txt

LAVORO=$DEST.lavoro
rm -rf "$LAVORO"
git clone -q --no-local --single-branch --branch main "$RADICE" "$LAVORO"
cd "$LAVORO"
git remote remove origin
# i tag del repo di lavoro puntano alla storia vecchia (email originale): nella copia non vanno
git tag -l | xargs -r git tag -d > /dev/null
: > "$MAPPA"
export EMAIL_PUBBLICA MAPPA
git filter-branch -f \
  --env-filter 'export GIT_AUTHOR_EMAIL="$EMAIL_PUBBLICA" GIT_COMMITTER_EMAIL="$EMAIL_PUBBLICA"' \
  --index-filter "git rm -r -q --cached --ignore-unmatch $ESCLUSI" \
  --commit-filter 'n=$(git commit-tree "$@"); echo "$GIT_COMMIT $n" >> "$MAPPA"; echo "$n"' \
  -- main
git update-ref -d refs/original/refs/heads/main
git reflog expire --expire=now --all
git gc -q --prune=now --aggressive

# controlli
test -z "$(git log --format='%ae%n%ce' | grep -v -x "$EMAIL_PUBBLICA" || true)" || { echo 'ERRORE: email non anonime'; exit 1; }
for f in $ESCLUSI; do
  test -z "$(git log --all --format=%H -- "$f")" || { echo "ERRORE: $f ancora nella storia"; exit 1; }
done
test -z "$(git for-each-ref --format='%(refname)' | grep -v -x 'refs/heads/main' || true)" || { echo 'ERRORE: riferimenti oltre main'; exit 1; }
test -z "$(git log --all --format='%ae%n%ce' | grep -v -x "$EMAIL_PUBBLICA" || true)" || { echo 'ERRORE: email non anonime in qualche riferimento'; exit 1; }
test -z "$(git rev-list --objects --all | grep -E '(note_revisore_v1_(EN|IT)\.md|VERIFICA_NOTE_REVISORE\.md|white_paper/(zenodo|linkedin))' || true)" || { echo 'ERRORE: oggetti delle note ancora presenti'; exit 1; }
echo "commit: $(git rev-list --count main); mappa: $(wc -l < "$MAPPA") righe"

rm -rf "$DEST"
mv "$LAVORO" "$DEST"
echo "copia pronta in $DEST"
