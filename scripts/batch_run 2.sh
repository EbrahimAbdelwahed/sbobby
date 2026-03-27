#!/bin/bash
# Batch processing: tutti gli audio → pipeline completa via Groq
# Lanciare con: ./batch_run.sh
# Log completo in: batch_run.log

set -uo pipefail

cd "$(dirname "$0")"
PROJECT_ROOT="$(pwd)"
LOG="$PROJECT_ROOT/batch_run.log"

# Usa il python dell'env conda sbobine direttamente
PYTHON="/opt/homebrew/Caskroom/miniforge/base/envs/sbobine/bin/python"

# Carica API keys
source ~/.zshrc 2>/dev/null || true

# Verifica API keys
if [ -z "${GROQ_API_KEY:-}" ]; then
    echo "ERRORE: GROQ_API_KEY non impostata" | tee "$LOG"
    exit 1
fi
if [ -z "${DEEPSEEK_API_KEY:-}" ]; then
    echo "ERRORE: DEEPSEEK_API_KEY non impostata" | tee "$LOG"
    exit 1
fi

# Lista lezioni: subject lesson audio_path
LESSONS=(
    "anatomia    lezione_01  audio/anatomia/lezione 1.m4a"
    "anatomia    lezione_02  audio/anatomia/lezione_2.m4a"
    "biochimica  lezione_01  audio/biochimica/lezione_1.m4a"
    "biochimica  lezione_02  audio/biochimica/lezione_2.m4a"
    "biochimica  lezione_03  audio/biochimica/lezione_3.m4a"
    "istologia   lezione_01  audio/istologia/lezione 1.m4a"
)

TOTAL=${#LESSONS[@]}
PASSED=0
FAILED=0
FAILED_LIST=""

echo "============================================================" | tee "$LOG"
echo "  BATCH RUN — $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG"
echo "  $TOTAL lezioni da processare (trascrizione Groq)" | tee -a "$LOG"
echo "============================================================" | tee -a "$LOG"

for i in "${!LESSONS[@]}"; do
    entry="${LESSONS[$i]}"
    # Parse: subject e lesson sono le prime 2 parole, il resto è il path audio
    subject=$(echo "$entry" | awk '{print $1}')
    lesson=$(echo "$entry" | awk '{print $2}')
    audio_path=$(echo "$entry" | sed "s/^[[:space:]]*${subject}[[:space:]]*${lesson}[[:space:]]*//" )

    N=$((i + 1))
    echo "" | tee -a "$LOG"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG"
    echo "  [$N/$TOTAL] $subject / $lesson" | tee -a "$LOG"
    echo "  Audio: $audio_path" | tee -a "$LOG"
    echo "  Inizio: $(date '+%H:%M:%S')" | tee -a "$LOG"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG"

    if $PYTHON src/pipeline.py run "$subject" "$lesson" "$audio_path" --groq 2>&1 | tee -a "$LOG"; then
        PASSED=$((PASSED + 1))
        echo "  ✓ [$N/$TOTAL] $subject/$lesson completato ($(date '+%H:%M:%S'))" | tee -a "$LOG"
    else
        FAILED=$((FAILED + 1))
        FAILED_LIST="$FAILED_LIST  - $subject/$lesson\n"
        echo "  ✗ [$N/$TOTAL] $subject/$lesson FALLITO ($(date '+%H:%M:%S'))" | tee -a "$LOG"
        echo "  Continuo con la prossima lezione..." | tee -a "$LOG"
    fi
done

echo "" | tee -a "$LOG"
echo "============================================================" | tee -a "$LOG"
echo "  BATCH COMPLETATO — $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG"
echo "  Successo: $PASSED/$TOTAL" | tee -a "$LOG"
if [ $FAILED -gt 0 ]; then
    echo "  Falliti: $FAILED" | tee -a "$LOG"
    echo -e "$FAILED_LIST" | tee -a "$LOG"
fi
echo "  Log completo: $LOG" | tee -a "$LOG"
echo "============================================================" | tee -a "$LOG"
