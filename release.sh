#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
task_version=$(python3 ./omarchy-limine-theme --version | cut -d ' ' -f2)
[[ ${RELEASE_TAG:-v$task_version} == "v$task_version" ]] || {
  echo 'Release tag does not match the program version.' >&2; exit 1;
}
git diff --quiet HEAD -- || { echo 'Commit changes before packaging.' >&2; exit 1; }
task_name="omarchy-limine-theme-$task_version"
mkdir -p dist
git archive --format=tar --prefix="$task_name/" HEAD | gzip -n > "dist/$task_name.tar.gz"
task_test=$(mktemp -d)
trap 'rm -rf "$task_test"' EXIT
tar -xzf "dist/$task_name.tar.gz" -C "$task_test"
python3 "$task_test/$task_name/test_theme.py"
bash -n "$task_test/$task_name/"{install.sh,uninstall.sh,theme-set.hook,boot-menu.hook,release.sh}
test -x "$task_test/$task_name/install.sh"
test -x "$task_test/$task_name/omarchy-limine-theme"
cd dist
sha256sum "$task_name.tar.gz" > SHA256SUMS
sha256sum -c SHA256SUMS
echo "Built $task_name.tar.gz"
