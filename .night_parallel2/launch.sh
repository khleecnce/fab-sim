#!/bin/bash
cd ~/fab-sim
export CLAUDE_CODE_OAUTH_TOKEN
D=.night_parallel2
for a in padmat padlife wafmet; do
  nohup claude -p "$(cat $D/$a.txt)" --model claude-fable-5-1 --max-turns 120 --permission-mode bypassPermissions --add-dir /Users/khleecnce/fab-sim > $D/$a.log 2>&1 &
  echo "$a $!" >> $D/pids.txt
done
wait
