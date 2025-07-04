#!/bin/bash

set -e

# Setup test environment
echo "🔧 Setting up test repo"
rm -rf test-repo
mkdir test-repo
cd test-repo

vctrl init

echo "hello" > test.txt
vctrl add test.txt
vctrl commit -m "Initial commit"

# Test branch creation and checkout
vctrl branch -b feature
vctrl checkout feature
echo "feature change" > feature.txt
vctrl add feature.txt
vctrl commit -m "Feature commit"

# Switch back to main and diff
echo "🔁 Switching back to main"
vctrl checkout main
vctrl diff

# Merge feature into main
vctrl merge main feature

# Edge Case: Try committing with no changes
echo "🧪 Committing with no changes (expect message)"
vctrl commit -m "No changes"

# Edge Case: Try adding a nonexistent file
echo "🧪 Adding nonexistent file"
vctrl add nofile.txt || echo "✅ Correctly handled missing file"

# Edge Case: Try switching to a nonexistent branch
echo "🧪 Switching to invalid branch"
vctrl checkout nonexistent || echo "✅ Correctly handled invalid branch"

# Test diff after modifying a file
echo "edit" >> test.txt
vctrl diff

# Test diff after deleting a file
rm feature.txt
vctrl diff

# Edge Case: Create merge conflict
vctrl checkout feature
echo "conflict on feature" > test.txt
vctrl add test.txt
vctrl commit -m "Conflicting change on feature"
vctrl checkout main
echo "conflict on main" > test.txt
vctrl add test.txt
vctrl commit -m "Conflicting change on main"

# Now merge to cause conflict
vctrl merge main feature

vctrl status

# Done
echo "✅ All tests completed"

