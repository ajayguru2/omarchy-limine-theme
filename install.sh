#!/usr/bin/env bash
set -euo pipefail
task_source=$(cd -- "$(dirname -- "$0")" && pwd)
if [[ ${1:-} == --system ]]; then
  [[ $EUID == 0 ]] || exit 1
  test -x /etc/boot/hooks/post.d/90-limine-enroll-config || {
    echo 'Missing Omarchy post-update signing hook.' >&2; exit 1;
  }
  install -o root -g root -m 0755 "$task_source/omarchy-limine-theme" /usr/local/bin/omarchy-limine-theme
  install -o root -g root -m 0755 "$task_source/boot-menu.hook" /etc/boot/hooks/post.d/85-omarchy-limine-menu
  exit
fi
[[ $EUID != 0 ]] || { echo 'Run ./install.sh as your desktop user.' >&2; exit 1; }
for task_command in python pkexec limine-enroll-config sbverify omarchy-hook-install; do
  command -v "$task_command" >/dev/null || { echo "Missing dependency: $task_command" >&2; exit 1; }
done
python -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else "Python 3.11 or newer is required")'
pkexec /bin/bash "$task_source/install.sh" --system
task_hook="$HOME/.config/omarchy/hooks/theme-set.d/omarchy-limine-theme.hook"
mkdir -p "$(dirname "$task_hook")"
install -m 0755 "$task_source/theme-set.hook" "$task_hook"
echo 'Installed. Run omarchy-limine-theme preview, then omarchy-limine-theme sync.'
