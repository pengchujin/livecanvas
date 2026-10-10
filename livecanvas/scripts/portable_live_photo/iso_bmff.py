# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 杨振
from __future__ import annotations

import struct
from dataclasses import dataclass


CONTAINER_TYPES = {
    b"moov",
    b"trak",
    b"mdia",
    b"minf",
    b"dinf",
    b"stbl",
    b"edts",
    b"tref",
    b"gmhd",
    b"udta",
    b"ilst",
}


@dataclass(frozen=True, slots=True)
class Atom:
    start: int
    size: int
    type: bytes
    header_size: int = 8

    @property
    def end(self) -> int:
        return self.start + self.size

    @property
    def payload_start(self) -> int:
        return self.start + self.header_size

    def raw(self, data: bytes | bytearray) -> bytes:
        return bytes(data[self.start : self.end])


def atom(kind: bytes, payload: bytes) -> bytes:
    if len(kind) != 4:
        raise ValueError("ISO-BMFF atom 类型必须是 4 字节")
    size = len(payload) + 8
    if size <= 0xFFFFFFFF:
        return struct.pack(">I4s", size, kind) + payload
    return struct.pack(">I4sQ", 1, kind, len(payload) + 16) + payload


def parse_atoms(data: bytes | bytearray, start: int = 0, end: int | None = None) -> list[Atom]:
    boundary = len(data) if end is None else end
    if start < 0 or boundary > len(data) or start > boundary:
        raise ValueError("ISO-BMFF 解析范围无效")
    result: list[Atom] = []
    position = start
    while position < boundary:
        if position + 8 > boundary:
            raise ValueError("ISO-BMFF atom 头部不完整")
        size = int.from_bytes(data[position : position + 4], "big")
        kind = bytes(data[position + 4 : position + 8])
        header = 8
        if size == 1:
            if position + 16 > boundary:
                raise ValueError("ISO-BMFF 64 位 atom 头部不完整")
            size = int.from_bytes(data[position + 8 : position + 16], "big")
            header = 16
        elif size == 0:
            size = boundary - position
        if size < header or position + size > boundary:
            label = kind.decode("latin-1", errors="replace")
            raise ValueError(f"ISO-BMFF atom {label} 超出文件边界")
        result.append(Atom(position, size, kind, header))
        position += size
    return result


def child_atoms(data: bytes | bytearray, parent: Atom) -> list[Atom]:
    return parse_atoms(data, parent.payload_start, parent.end)


def first_child(data: bytes | bytearray, parent: Atom, kind: bytes) -> Atom | None:
    return next((item for item in child_atoms(data, parent) if item.type == kind), None)


def walk_atoms(data: bytes | bytearray, parent: Atom) -> list[Atom]:
    found: list[Atom] = []
    for item in child_atoms(data, parent):
        found.append(item)
        if item.type in CONTAINER_TYPES:
            found.extend(walk_atoms(data, item))
    return found


def patch_chunk_offsets(moov: bytes, delta: int) -> bytes:
    """Shift every stco/co64 entry in a complete moov atom by a constant."""
    payload = bytearray(moov)
    top = parse_atoms(payload)
    if len(top) != 1 or top[0].type != b"moov":
        raise ValueError("需要一个完整的 moov atom")

    def visit(parent: Atom) -> None:
        for item in child_atoms(payload, parent):
            if item.type in {b"stco", b"co64"}:
                count_at = item.payload_start + 4
                if count_at + 4 > item.end:
                    raise ValueError("MOV chunk offset 表不完整")
                count = int.from_bytes(payload[count_at : count_at + 4], "big")
                width = 4 if item.type == b"stco" else 8
                entries = count_at + 4
                if entries + count * width > item.end:
                    raise ValueError("MOV chunk offset 条目超出 atom")
                for index in range(count):
                    position = entries + index * width
                    old = int.from_bytes(payload[position : position + width], "big")
                    new = old + delta
                    if new < 0 or new >= 1 << (width * 8):
                        raise ValueError("MOV chunk offset 调整后越界")
                    payload[position : position + width] = new.to_bytes(width, "big")
            elif item.type in CONTAINER_TYPES:
                visit(item)

    visit(top[0])
    return bytes(payload)
