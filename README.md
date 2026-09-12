# Omarchy Limine Theme

Carry your Omarchy wallpaper and palette into the boot menu.

This first version is a **hook-based Omarchy extension**, installed with the script below. It is not yet a Quattro shell/marketplace plugin and does not use `omarchy plugin add`.

## What it does

- Reads the selected theme's `colors.toml` and current background.
- Updates Limine's wallpaper, palette, and accent colors.
- Preserves boot entries, kernel parameters, branding, font size, timeout, and default OS.
- Uses Omarchy's boot-partition lock and `limine-enroll-config` signing workflow.
- Checks that the local sbctl certificate is enrolled when Secure Boot is enabled.
- Restores both the configuration and EFI executable if applying/signing fails.
- Retains three recovery copies and cleans up unreferenced wallpapers created by this tool.

No daemon, Python packages, firmware key changes, kernel rebuilds, or passwordless sudo rules.

## Requirements

Omarchy with Python 3.11+, Polkit, `limine-enroll-config`, `sbverify`, and x86-64 Limine installed at `/boot/EFI/limine/limine_x64.efi`. The FAT32 EFI partition must be mounted at `/boot`.

Secure Boot must already work. If enabled, this version expects sbctl's default certificate at `/var/lib/sbctl/keys/db/db.pem`, enrolled in firmware `db`. It does not set up keys or repair bootloaders.

## Install

Review the source, then run as your normal desktop user:

```sh
chmod +x install.sh uninstall.sh
./install.sh
omarchy-limine-theme preview
omarchy-limine-theme sync
```

Installation copies the Python executable into `/usr/local/bin` as root and installs `~/.config/omarchy/hooks/theme-set.d/omarchy-limine-theme.hook`.

Changing a theme invokes the hook. **Expect a system authentication prompt** for boot-file access; cancelling leaves the current boot appearance in place. No unattended administrative access is granted.

Changing only the wallpaper does not trigger Omarchy's `theme-set` hook. Run `omarchy-limine-theme sync` after cycling wallpapers. A future shell integration can handle that event without polling.

## Commands

```sh
omarchy-limine-theme preview   # show the proposed config diff; no boot writes
omarchy-limine-theme sync      # apply the current theme
omarchy-limine-theme rollback  # restore the previous appearance, keeping current OS entries
python test_theme.py           # exercise a temporary fake ESP, including signing failure
./uninstall.sh                # remove tool/hook; retain boot appearance and recovery files
```

Preview also needs authentication because Omarchy protects `limine.conf` from user reads. Wallpaper bytes are sent over stdin, never as a root command or an arbitrary destination path. The privileged side accepts only hex colors and supported image signatures, writes only its managed appearance fields, and never executes theme-provided code.

Supported wallpapers: static PNG, JPEG, BMP, QOI, up to 32 MiB. This tool copies them without conversion. Animated/video formats are unsupported. Firmware ultimately decodes the image; only use trusted wallpapers. Existing layout and branding remain yours. Appearance options must be in the global header before the first OS entry.

## Recovery and limits

Backups are under `/var/lib/omarchy-limine-theme/backup-*`. `latest` identifies the most recent successful operation's pre-change backup. Automatic failure recovery restores the exact pre-change configuration and EFI executable. The manual `rollback` command restores appearance fields onto the **current** configuration and re-signs, so it does not reintroduce outdated kernel paths.

The shared lock coordinates with Omarchy tools using `/run/lock/boot-partition.lock`; unrelated programs that ignore it are not serialized. An abrupt power loss during EFI signing cannot be recovered by a running process: boot recovery media and restore the matching config/EFI backup pair if needed. The two files are not a filesystem-wide atomic transaction.

Changing themes does not enroll new certificates, touch Windows Boot Manager, or modify OS entries. Initial testing covers this machine's configured Limine + sbctl stack; other firmware needs boot testing. Firmware rendering can only be confirmed after reboot.

## References

- [Omarchy](https://github.com/omacom/omarchy)
- [Limine configuration](https://github.com/limine-bootloader/limine/blob/v12.x/CONFIG.md)
- [sbctl](https://github.com/Foxboron/sbctl)

License: MIT.
