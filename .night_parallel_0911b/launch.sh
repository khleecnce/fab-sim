#!/bin/bash
cd /Users/khleecnce/fab-sim
export CLAUDE_CODE_OAUTH_TOKEN
D=.night_parallel_0911b
pids=""
for a in cmp-data-engineer film-w slurry-chemistry; do
  claude -p "$(cat $D/$a.txt)" --model claude-opus-4-8 --permission-mode bypassPermissions --add-dir /Users/khleecnce/fab-sim > $D/$a.log 2>&1 &
  pid=$!
  echo "$a pid=$pid"
  pids="$pids $pid"
done
echo "PIDS:$pids" > $D/pids.txt
wait
echo "ALL_DONE"
