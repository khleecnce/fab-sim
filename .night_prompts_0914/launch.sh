#!/bin/bash
D=/Users/khleecnce/fab-sim/.night_prompts_0914
cd /Users/khleecnce/fab-sim
for a in defect-scientist slurry-colloid tool-post-clean; do
  claude -p "$(cat $D/$a.txt)" --model claude-opus-4-8 --dangerously-skip-permissions --max-turns 80 --add-dir /Users/khleecnce/fab-sim > $D/$a.log 2>&1 &
  echo "$a $!" >> $D/pids.txt
done
wait
