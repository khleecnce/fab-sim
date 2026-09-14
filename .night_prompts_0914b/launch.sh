#!/bin/bash
D=/Users/khleecnce/fab-sim/.night_prompts_0914b
cd /Users/khleecnce/fab-sim
source ~/.hermes/.env; export CLAUDE_CODE_OAUTH_TOKEN
pids=()
for a in defect-scientist film-w film-nitride; do
  claude -p "$(cat $D/$a.txt)" --model claude-opus-4-8 --dangerously-skip-permissions --max-turns 80 --add-dir /Users/khleecnce/fab-sim > $D/$a.log 2>&1 &
  pids+=($!); echo "$a $!" >> $D/pids.txt
done
wait "${pids[@]}"
echo ALLDONE >> $D/launch.log
