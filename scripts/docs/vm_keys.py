"""Kirim ketikan ke konsol VM VirtualBox (scancode set 1) - untuk GRUB/root shell."""
import subprocess
import sys
import time

VBM = r'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe'

MAP = {
    'a': 0x1e, 'b': 0x30, 'c': 0x2e, 'd': 0x20, 'e': 0x12, 'f': 0x21, 'g': 0x22,
    'h': 0x23, 'i': 0x17, 'j': 0x24, 'k': 0x25, 'l': 0x26, 'm': 0x32, 'n': 0x31,
    'o': 0x18, 'p': 0x19, 'q': 0x10, 'r': 0x13, 's': 0x1f, 't': 0x14, 'u': 0x16,
    'v': 0x2f, 'w': 0x11, 'x': 0x2d, 'y': 0x15, 'z': 0x2c,
    '1': 0x02, '2': 0x03, '3': 0x04, '4': 0x05, '5': 0x06, '6': 0x07, '7': 0x08,
    '8': 0x09, '9': 0x0a, '0': 0x0b,
    ' ': 0x39, '/': 0x35, '-': 0x0c, '=': 0x0d, '.': 0x34, ',': 0x33,
    '\n': 0x1c, '\t': 0x0f,
    '[': 0x1a, ']': 0x1b, ';': 0x27, "'": 0x28, '`': 0x29, '\\': 0x2b,
}
SHIFTED = {
    ':': 0x27, '_': 0x0c, '>': 0x34, '<': 0x33, '"': 0x28, '|': 0x2b,
    '(': 0x0a, ')': 0x0b, '*': 0x09, '!': 0x02, '@': 0x03, '#': 0x04, '$': 0x05,
    '%': 0x06, '^': 0x07, '&': 0x08, '?': 0x35, '+': 0x0d, '{': 0x1a, '}': 0x1b,
}
SHIFT = 0x2a
CTRL = 0x1d
ESC = 0x01
DOWN = (0xe0, 0x50)
END = (0xe0, 0x4f)


def codes_for(text):
    out = []
    for ch in text:
        if ch.isalpha() and ch.isupper():
            out.append((SHIFT, MAP[ch.lower()]))
        elif ch in MAP:
            out.append((MAP[ch],))
        elif ch in SHIFTED:
            out.append((SHIFT, SHIFTED[ch]))
        else:
            raise SystemExit(f'karakter tidak didukung: {ch!r}')
    return out


def send(vm, seq, delay=0.02, chunk=60):
    """seq: list of tuples of scancodes (make), break codes ditambahkan otomatis."""
    flat = []
    for tup in seq:
        mods = list(tup[:-1])
        key = tup[-1]
        flat.extend(mods)
        flat.append(key)
        flat.append(key | 0x80)
        for m in reversed(mods):
            flat.append(m | 0x80)
    for i in range(0, len(flat), chunk):
        part = flat[i:i + chunk]
        subprocess.run([VBM, 'controlvm', vm, 'keyboardputscancode'] + [f'{b:02x}' for b in part],
                       check=False, capture_output=True)
        time.sleep(delay)


def type_text(vm, text, delay=0.03):
    send(vm, codes_for(text), delay=delay)


def press(vm, *tuples):
    send(vm, list(tuples), delay=0.05)


if __name__ == '__main__':
    vm = sys.argv[1]
    mode = sys.argv[2]
    if mode == 'text':
        type_text(vm, sys.argv[3])
    elif mode == 'esc':
        press(vm, (ESC,), (ESC,), (ESC,))
    elif mode == 'enter':
        press(vm, ('\n',) if False else (0x1c,))
    elif mode == 'ctrlx':
        send(vm, [(CTRL, 0x2d)])
    elif mode == 'grabmenu':
        for _ in range(12):
            press(vm, (ESC,))
            time.sleep(0.15)
    elif mode == 'edit':
        send(vm, [DOWN, DOWN, END])
