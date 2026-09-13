# v0.1.0 — Initial prerelease

An Omarchy hook-based extension that carries the selected wallpaper and palette into Limine.

- Theme-change syncing with a normal administrator authentication prompt.
- Wallpaper hashes, existing Secure Boot signing integration, and recovery copies.
- Optional direct Omarchy and Windows choices with a separate recovery menu.
- Kernel-update hook to refresh the direct shortcut.
- Preview, appearance rollback, menu removal, and uninstall commands.
- Tests covering input validation, entry preservation, kernel-target refresh, signing failure recovery, and backup retention.

## Install

Download `omarchy-limine-theme-0.1.0.tar.gz` and `SHA256SUMS` below, verify with `sha256sum -c SHA256SUMS`, extract the archive, and run `./install.sh` as your desktop user. See the included README for prerequisites and usage.

## Compatibility and current limits

Requires Omarchy, Python 3.11+, and x86-64 Limine on a FAT32 ESP mounted at `/boot`. Secure Boot must already be configured if enabled. Version 0.1.0 is an initial prerelease with limited hardware coverage.

This is a hook-based extension, not a Quattro marketplace package. Theme changes request administrator authentication. Wallpaper-only changes require `omarchy-limine-theme sync`. The optional direct menu expects a primary `linux` EFI/UKI entry. No bootloader binaries, firmware keys, or wallpapers are bundled.
