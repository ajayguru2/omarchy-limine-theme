"""Run with python test_theme.py; never accesses the real boot partition."""
import base64
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile

source = Path(__file__).with_name('omarchy-limine-theme')
loader = importlib.machinery.SourceFileLoader('theme', str(source))
spec = importlib.util.spec_from_loader(loader.name, loader)
theme = importlib.util.module_from_spec(spec)
loader.exec_module(theme)

COLORS = {'background': '#14151b', 'foreground': '#f8f8f2', 'accent': '#8be9fd'}
# A complete one-pixel PNG.
IMAGE = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jZ1kAAAAASUVORK5CYII=')
CONFIG = ('timeout: 30\ndefault_entry: Omarchy/linux\ninterface_branding: My computer\n'
          'interface_branding_colour: aaaaaa\ninterface_branding_color: bbbbbb\n'
          '/+Omarchy\n  //linux\n  protocol: efi\n  path: boot():/kernel.efi#1234\n'
          '  cmdline: cryptdevice=UUID=keep-this root=keep-this\n'
          '/Windows\n protocol: efi_boot_entry\n entry: Windows Boot Manager\n')


def rejects(call):
    try:
        call()
    except (ValueError, TypeError):
        return
    raise AssertionError('Unsafe input was accepted')


def check():
    payload = {'colors': COLORS, 'image': base64.b64encode(IMAGE).decode()}
    assert theme.decode_payload(json.dumps(payload)) == (COLORS, IMAGE, 'png')
    values = theme.appearance(COLORS, IMAGE, 'png')
    updated = theme.render(CONFIG, values)
    assert theme.split_config(updated)[1] == theme.split_config(CONFIG)[1]
    assert 'interface_branding: My computer\n' in updated
    assert 'timeout: 30\ndefault_entry: Omarchy/linux\n' in updated
    assert theme.render(updated, values) == updated
    assert updated.count('interface_branding_color:') == 1
    assert 'interface_branding_colour:' not in updated
    new_kernel = updated.replace('kernel.efi#1234', 'new-kernel.efi#5678')
    restored = theme.restore_appearance(new_kernel, CONFIG)
    assert theme.split_config(restored)[1] == theme.split_config(new_kernel)[1]
    assert 'interface_branding_color: bbbbbb' in restored
    assert 'wallpaper:' not in restored
    rejects(lambda: theme.render(CONFIG + 'wallpaper: boot():/other.png\n', values))
    rejects(lambda: theme.decode_payload(json.dumps({**payload, 'command': 'bad'})))
    rejects(lambda: theme.decode_payload(json.dumps({**payload, 'colors': {**COLORS, 'accent': '#ffffff\ntimeout: 0'}})))
    rejects(lambda: theme.decode_payload(json.dumps({**payload, 'image': 'not base64!'})))
    rejects(lambda: theme.image_type(b'not a wallpaper'))
    rejects(lambda: theme.image_type(IMAGE[:16] + b'\xff' * 8 + IMAGE[24:]))
    generated = CONFIG.replace('/+Omarchy\n', '/+Omarchy\ncomment: machine-id=test-machine\n')
    generated = generated.replace('  //linux\n', '  //linux\n  comment: kernel-id=linux\n')
    generated = generated.replace('/Windows\n', '  //Snapshots\n   ///Yesterday\n    ////linux\n    protocol: efi\n    path: boot():/old.efi\n/Windows\n')
    direct = theme.direct_menu(generated, 'test-machine')
    assert theme.direct_menu(direct, 'test-machine') == direct
    assert '/Omarchy\ncomment: omarchy-limine-theme-direct\n' in direct
    assert 'default_entry: Omarchy\n' in direct
    assert '/Recovery & snapshots\ncomment: machine-id=test-machine\n' in direct
    assert direct.index('/Omarchy\n') < direct.index('/Windows\n') < direct.index('/Recovery & snapshots\n')
    assert direct.split('/Windows\n')[1].split('/Recovery & snapshots\n')[0] == generated.split('/Windows\n')[1]
    assert direct.count('path: boot():/old.efi') == 1
    direct_head, canonical = direct.split('/Recovery & snapshots\n')
    refreshed = theme.direct_menu(direct_head + '/Recovery & snapshots\n' + canonical.replace('kernel.efi#1234', 'new-kernel.efi#5678'), 'test-machine')
    assert 'path: boot():/new-kernel.efi#5678' in refreshed.split('/Windows\n')[0]
    assert 'path: boot():/kernel.efi#1234' not in refreshed
    disabled = theme.remove_direct_menu(refreshed)
    assert theme.MENU_MARKER not in disabled
    assert 'timeout: no\n' in disabled
    assert '/+Omarchy\ncomment: machine-id=test-machine\n' in disabled
    assert theme.remove_direct_menu(disabled) == disabled
    rejects(lambda: theme.direct_menu(generated, 'wrong-machine'))
    rejects(lambda: theme.direct_menu(generated.replace('kernel-id=linux', 'kernel-id=linux-lts'), 'test-machine'))
    with tempfile.TemporaryDirectory() as directory:
        theme.BOOT = Path(directory) / 'boot'
        theme.STATE = Path(directory) / 'state'
        (theme.BOOT / theme.EFI).parent.mkdir(parents=True)
        (theme.BOOT / theme.CONFIG).write_text(CONFIG)
        (theme.BOOT / theme.EFI).write_bytes(b'known-good-signed-efi')
        filename = values['wallpaper'].split('/')[1].split('#')[0]

        def fail_signing():
            (theme.BOOT / theme.EFI).write_bytes(b'partially-written-efi')
            raise RuntimeError('simulated signing failure')

        try:
            theme.apply_transaction(updated, IMAGE, filename, signer=fail_signing)
        except RuntimeError:
            pass
        else:
            raise AssertionError('Signing failure was swallowed')
        assert (theme.BOOT / theme.CONFIG).read_text() == CONFIG
        assert (theme.BOOT / theme.EFI).read_bytes() == b'known-good-signed-efi'
        assert not (theme.BOOT / filename).exists()
        assert not (theme.STATE / 'latest').exists()
        theme.apply_transaction(updated, IMAGE, filename, signer=lambda: None)
        assert (theme.BOOT / theme.CONFIG).read_text() == updated
        assert (theme.BOOT / filename).read_bytes() == IMAGE
        assert (theme.STATE / 'latest').is_file()
        for _ in range(4):
            theme.apply_transaction(updated, IMAGE, filename, signer=lambda: None)
        assert len(list(theme.STATE.glob('backup-*'))) == 3
    print('PASS: palette validation, entry preservation, idempotence, direct menu refresh/removal, signing failure recovery, and backup retention')


if __name__ == '__main__':
    check()
