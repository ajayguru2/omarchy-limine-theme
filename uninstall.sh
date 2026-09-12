#!/usr/bin/env bash
set -euo pipefail
[[ $EUID != 0 ]] || { echo 'Run ./uninstall.sh as your desktop user.' >&2; exit 1; }
# Keep the last working appearance and recovery files intact.
pkexec /usr/bin/rm -f /usr/local/bin/omarchy-limine-theme
rm -f "$HOME/.config/omarchy/hooks/theme-set.d/omarchy-limine-theme.hook"
echo 'Removed the tool and hook. Existing boot appearance and backups remain.'
