#!/bin/bash
REMOTE="origin"
BRANCH="main"
CHUNK_SIZE=200

commits=($(git log --reverse --format="%H"))
total=${#commits[@]}
echo "Total commits to push in chunks: $total"

for ((i=$CHUNK_SIZE-1; i<$total; i+=$CHUNK_SIZE)); do
    commit="${commits[$i]}"
    echo "======================================"
    echo "Pushing chunk ending at commit $commit (Index: $i)"
    git push --force $REMOTE $commit:refs/heads/$BRANCH
    if [ $? -ne 0 ]; then
        echo "Push failed at commit $commit"
        exit 1
    fi
done

echo "Pushing final HEAD..."
git push --force $REMOTE HEAD:refs/heads/$BRANCH
echo "Done!"
