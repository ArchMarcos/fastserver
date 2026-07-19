"""Minimal pure-Python MessagePack decoder (no external deps).

Supports the subset needed for PortunusDB responses:
nil, bool, ints, floats, str, bin, arrays, maps.
"""

from __future__ import annotations
from struct import unpack_from
from typing import Any


def decode(data: bytes, offset: int = 0) -> tuple[Any, int]:
    """Decode one msgpack value at ``offset``. Return ``(value, new_offset)``.

    Raise ValueError on truncated or unsupported input.
    """
    if offset >= len(data):
        raise ValueError("truncated msgpack input")

    b = data[offset]
    offset += 1

    # ── positive fixint / fixmap / fixarray / fixstr ──
    if b <= 0x7F:
        return b, offset
    if b >= 0xE0:
        return b - 256, offset

    # ── fixmap ──
    if 0x80 <= b <= 0x8F:
        return _decode_map(data, offset, b & 0x0F)
    # ── fixarray ──
    if 0x90 <= b <= 0x9F:
        return _decode_array(data, offset, b & 0x0F)
    # ── fixstr ──
    if 0xA0 <= b <= 0xBF:
        n = b & 0x1F
        end = offset + n
        _check(data, end)
        return data[offset:end].decode("utf-8"), end

    # ── nil / false / true ──
    if b == 0xC0:
        return None, offset
    if b == 0xC2:
        return False, offset
    if b == 0xC3:
        return True, offset

    # ── bin 8/16/32 ──
    if b == 0xC4:
        n = data[offset]; offset += 1
    elif b == 0xC5:
        n = unpack_from(">H", data, offset)[0]; offset += 2
    elif b == 0xC6:
        n = unpack_from(">I", data, offset)[0]; offset += 4
    else:
        return _decode_explicit(b, data, offset)

    end = offset + n
    _check(data, end)
    return data[offset:end], end


def _decode_explicit(b: int, data: bytes, offset: int) -> tuple[Any, int]:
    # ── floats ──
    if b == 0xCA:  # float32
        v = unpack_from(">f", data, offset)[0]; return v, offset + 4
    if b == 0xCB:  # float64
        v = unpack_from(">d", data, offset)[0]; return v, offset + 8

    # ── uint ──
    if b == 0xCC:
        return data[offset], offset + 1
    if b == 0xCD:
        return unpack_from(">H", data, offset)[0], offset + 2
    if b == 0xCE:
        return unpack_from(">I", data, offset)[0], offset + 4
    if b == 0xCF:
        return unpack_from(">Q", data, offset)[0], offset + 8

    # ── int ──
    if b == 0xD0:
        v = unpack_from(">b", data, offset)[0]; return v, offset + 1
    if b == 0xD1:
        return unpack_from(">h", data, offset)[0], offset + 2
    if b == 0xD2:
        return unpack_from(">i", data, offset)[0], offset + 4
    if b == 0xD3:
        return unpack_from(">q", data, offset)[0], offset + 8

    # ── str 8/16/32 ──
    if b == 0xD9:
        n = data[offset]; offset += 1; end = offset + n
        _check(data, end); return data[offset:end].decode("utf-8"), end
    if b == 0xDA:
        n = unpack_from(">H", data, offset)[0]; offset += 2; end = offset + n
        _check(data, end); return data[offset:end].decode("utf-8"), end
    if b == 0xDB:
        n = unpack_from(">I", data, offset)[0]; offset += 4; end = offset + n
        _check(data, end); return data[offset:end].decode("utf-8"), end

    # ── array16/32 ──
    if b == 0xDC:
        n = unpack_from(">H", data, offset)[0]; offset += 2
        return _decode_array(data, offset, n)
    if b == 0xDD:
        n = unpack_from(">I", data, offset)[0]; offset += 4
        return _decode_array(data, offset, n)

    # ── map16/32 ──
    if b == 0xDE:
        n = unpack_from(">H", data, offset)[0]; offset += 2
        return _decode_map(data, offset, n)
    if b == 0xDF:
        n = unpack_from(">I", data, offset)[0]; offset += 4
        return _decode_map(data, offset, n)

    raise ValueError(f"unsupported msgpack byte: 0x{b:02x} at offset {offset - 1}")


def _decode_array(data: bytes, offset: int, n: int) -> tuple[list, int]:
    arr = []
    for _ in range(n):
        v, offset = decode(data, offset)
        arr.append(v)
    return arr, offset


def _decode_map(data: bytes, offset: int, n: int) -> tuple[dict, int]:
    m = {}
    for _ in range(n):
        k, offset = decode(data, offset)
        v, offset = decode(data, offset)
        m[k] = v
    return m, offset


def _check(data: bytes, end: int) -> None:
    if end > len(data):
        raise ValueError("truncated msgpack input")


def loads(data: bytes) -> Any:
    """Decode a single top-level msgpack value from bytes."""
    value, _ = decode(data, 0)
    return value