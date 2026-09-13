#!/bin/bash
cd /Users/khleecnce/fab-sim
export CLAUDE_CODE_OAUTH_TOKEN
D=.night_parallel_0911
pids=""
for a in film-poly-si film-nitride tool-endpoint; do
  claude -p "$(cat $D/$a.txt)" --model claude-opus-4-8 --permission-mode bypassPermissions --add-dir /Users/khleecnce/fab-sim > $D/$a.log 2>&1 &
  pid=$!
  echo "$a pid=$pid"
  pids="$pids $pid"
done
echo "PIDS:$pids" > $D/pids.txt
wait
echo "ALL_DONE"
