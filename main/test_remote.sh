#!/bin/bash
set -e

echo "🧪 Starting remote tests..."

# Clean previous test data
rm -rf remote-repo push-test fetch-test pull-test cloned-repo non-repo-dir

## --- Setup Remote Repo ---
mkdir remote-repo
cd remote-repo
vctrl init .
echo "initial" > file.txt
vctrl add file.txt
vctrl commit -m "Initial commit"
cd ..

## --- Test Clone ---
echo "🔍 Testing clone..."
vctrl clone remote-repo cloned-repo

if [ ! -f cloned-repo/file.txt ]; then
    echo "❌ Clone failed: file.txt not found"
    exit 1
fi
echo "✅ Clone passed"

## --- Test Fetch ---
echo "🔍 Testing fetch..."
mkdir fetch-test
cd fetch-test
vctrl init .
vctrl fetch ../remote-repo

REMOTE_REF=".vctrl/refs/remotes/../remote-repo/main"
if [ ! -f "$REMOTE_REF" ]; then
    echo "❌ Fetch failed: remote ref not found"
    exit 1
fi
cd ..
echo "✅ Fetch passed"

## --- Test Push ---
echo "🔍 Testing push..."
mkdir push-test
cd push-test
vctrl init .
echo "push content" > push.txt
vctrl add push.txt
vctrl commit -m "Push commit"
vctrl push ../remote-repo
cd ..

# Check if remote-repo received the commit
if ! grep -q "push content" remote-repo/push.txt 2>/dev/null; then
    echo "❌ Push failed: push.txt not in remote"
    exit 1
fi
echo "✅ Push passed"

## --- Test Pull ---
echo "🔍 Testing pull..."
mkdir pull-test
cd pull-test
vctrl init .
vctrl pull ../remote-repo
if [ ! -f "file.txt" ]; then
    echo "❌ Pull failed: file.txt not pulled"
    exit 1
fi
cd ..
echo "✅ Pull passed"

## --- Edge Case: Clone from non-repo ---
echo "🔍 Testing clone from non-repo..."
mkdir non-repo-dir
if vctrl clone ./non-repo-dir fake-clone; then
    echo "❌ Clone from non-repo should have failed"
    exit 1
fi
echo "✅ Clone from non-repo correctly failed"

## --- Edge Case: Fetch from non-repo ---
echo "🔍 Testing fetch from non-repo..."
mkdir fetch-test-bad
cd fetch-test-bad
vctrl init .
if vctrl fetch ../non-repo-dir; then
    echo "❌ Fetch from non-repo should have failed"
    exit 1
fi
cd ..
echo "✅ Fetch from non-repo correctly failed"

echo "🎉 All remote tests passed successfully!"

