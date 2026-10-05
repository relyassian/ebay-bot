#!/usr/bin/env bash
# Push the bot's committed state, retrying when another job pushed at the same moment.
# On a conflict in a data file, this run's (newer) version wins.
for i in 1 2 3 4 5; do
  git pull -q --rebase -X theirs && git push -q && exit 0
  git rebase --abort 2>/dev/null
  sleep $((i * 3))
done
echo "could not push state after 5 tries"; exit 1
