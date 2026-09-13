#!/usr/bin/env bash
set -euo pipefail
[[ $EUID != 0 ]] || { echo 'Run ./uninstall.sh as your desktop user.' >&2; exit 1; }
# Keep the last working appearance and recovery files intact.
if [[ -x /usr/local/bin/omarchy-limine-theme ]]; then
  /usr/local/bin/omarchy-limine-theme menu-off
fi
pkexec /usr/bin/rm -f /usr/local/bin/omarchy-limine-theme /etc/boot/hooks/post.d/85-omarchy-limine-menu
rm -f "$HOME/.config/omarchy/hooks/theme-set.d/omarchy-limine-theme.hook"
echo 'Removed the tool and hook. Existing boot appearance and backups remain.'
