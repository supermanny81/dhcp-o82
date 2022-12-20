from __future__ import annotations

import csv
import os
import re
from enum import IntEnum
from typing import Tuple, Union

from netaddr import EUI
from netaddr.core import AddrFormatError


class SubOptType(IntEnum):
    CIRCUIT_ID = 1
    REMOTE_ID = 2
    SUBSCRIBER_ID = 6
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN


class SubOptFormat(IntEnum):
    CIRCUIT_ID = 0
    HEX = 1
    STRING = 2


class Option82:
    def __init__(
        self,
        circuit_id: Union[str, Tuple[int, int, int]] = None,
        remote_id: str = None,
        subscriber_id: str = None,
    ) -> None:
        self.sub_option: dict[bytearray] = {}
        if circuit_id:
            self.set_circuit_id(circuit_id)
        if remote_id:
            self.set_remote_id(remote_id)
        if subscriber_id:
            self.set_subscriber_id(subscriber_id)
        self.delim = ":"

    @staticmethod
    def from_csv(file_in: str, file_out: str):
        out = []

        with open(file_in) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                o = Option82()
                if all(field in row.keys() for field in ["vlan", "module", "port"]):
                    o.set_circuit_id(
                        (int(row["vlan"]), int(row["module"]), int(row["port"]))
                    )
                elif "circuit_id" in row.keys():
                    o.set_circuit_id(row["circuit_id"])
                if "remote_id" in row.keys():
                    o.set_remote_id(row["remote_id"])
                if "subcriber_id" in row.keys():
                    o.set_subscriber_id(row["subscriber_id"])
                row["hex"] = o.to_hex()
                out.append(row)

        with open(file_out, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=out[0].keys())
            writer.writeheader()
            writer.writerows(out)

    @classmethod
    def from_hex(cls, hex_str: str) -> Option82:
        hex_str = re.sub("[\\\\:\\-\\\\.]", "", hex_str)
        ba = bytearray.fromhex(hex_str)
        o82 = cls()
        while ba:
            item = ba.pop(0)
            sub_opt_type = 0
            if item != 6:
                # remove length of option, since subsequent length def upcoming
                del ba[0:1]
                sub_opt_type = ba.pop(0)
            sub_opt_len = ba.pop(0)
            sub_opt_val = ba[0:sub_opt_len]
            del ba[0:sub_opt_len]
            o82.set_sub_option(item, sub_opt_val, sub_opt_type)
        return o82

    def set_sub_option(self, option: int, value: bytes, type: int) -> Option82:
        self.sub_option[option] = {"value": value, "type": type}
        return self

    def set_circuit_id(self, circuit_id: Union[str, Tuple[int, int, int]]) -> Option82:
        if isinstance(circuit_id, Tuple):
            vlan, module, port = circuit_id
            if all([vlan, module, port]):
                c1 = (vlan >> 8) & 0xFF
                c2 = vlan & 0xFF
                c3 = module & 0xFF
                c4 = port & 0xFF
                self.set_sub_option(1, bytearray([c1, c2, c3, c4]), 0)
        else:
            self.set_sub_option(1, circuit_id.encode("ascii"), 1)
        return self

    def set_remote_id(self, remote_id: str) -> Option82:
        try:
            self.set_sub_option(2, int(EUI(remote_id)).to_bytes(6, "big"), 0)
        except AddrFormatError:
            self.set_sub_option(2, remote_id.encode("ascii"), 1)
        return self

    def set_subscriber_id(self, subscriber_id: str) -> Option82:
        # most vendors truncate at 50 char
        subscriber_id = subscriber_id[:50]
        self.set_sub_option(6, subscriber_id.encode("ascii"), 1)
        return self

    def get_remote_id(self, opt_type: SubOptFormat = SubOptFormat.HEX) -> str:
        if opt_type == SubOptFormat.HEX:
            return self.sub_option[2]["value"].hex(self.delim)
        else:
            return self._sub_opt_to_string(2)

    def get_circuit_id(self, opt_type: SubOptFormat = SubOptFormat.CIRCUIT_ID) -> str:
        if opt_type == SubOptFormat.CIRCUIT_ID:
            if len(self.sub_option[1]["value"]) == 4:
                ba = self.sub_option[1]["value"]
                vlan = int.from_bytes(ba[0:2], "big")
                module = ba[2]
                port = ba[3]
                return f"{vlan}-{module}-{port}"
        elif opt_type == SubOptFormat.STRING:
            return self._sub_opt_to_string(1)
        else:
            return self.sub_option[1]["value"].hex(self.delim)

    def get_subscriber_id(self, opt_type: SubOptFormat = SubOptFormat.HEX) -> str:
        if opt_type == SubOptFormat.HEX:
            return self.sub_option[6].hex(self.delim)
        else:
            return self._sub_opt_to_string(6)

    def to_hex(self) -> str:
        ba = bytearray()
        for item in sorted(self.sub_option):
            option = bytearray()
            if item != 6:
                ol = len(self.sub_option[item]["value"]).to_bytes(1, "big")
                option.append(self.sub_option[item]["type"] & 0xFF)
                option += ol
            option += self.sub_option[item]["value"]
            ba.append(item & 0xFF)
            ba.append(len(option) & 0xFF)
            ba += option
        return ba.hex(self.delim).upper()

    def _sub_opt_to_string(self, num: int) -> str:
        try:
            out = self.sub_option[num]["value"].decode("ascii")
            if out.isprintable():
                return out
        except UnicodeDecodeError:
            pass

    def _sub_opt_details(self) -> str:
        out = self.to_hex()
        out += os.linesep * 2
        for key in sorted(self.sub_option.keys()):
            opt_len = len(self.sub_option[key]["value"])
            if key in (1, 2):
                opt_len += 2
            out += (
                f"sub-option: {key} ({hex(key)}), "
                f"name: {SubOptType(key).name}, "
                f"length: {opt_len} ({hex(opt_len)}){os.linesep}"
            )
            if key in (1, 2):
                out += (
                    f"  type: {self.sub_option[key]['type']} "
                    f"({hex(self.sub_option[key]['type'])}), length: {opt_len - 2} "
                    f"({hex(opt_len - 2)}){os.linesep}"
                )
            out += f"  val: {self.sub_option[key]['value'].hex(self.delim)}{os.linesep}"
            if key == 1:
                if self.get_circuit_id(SubOptFormat.CIRCUIT_ID) is not None:
                    out += (
                        f"  vlan-module-port: "
                        f"{self.get_circuit_id(SubOptFormat.CIRCUIT_ID)}"
                        f"{os.linesep}"
                    )
                if self.get_circuit_id(SubOptFormat.STRING) is not None:
                    out += (
                        f"  string: "
                        f"{self.get_circuit_id(SubOptFormat.STRING)}{os.linesep}"
                    )
            else:
                if self._sub_opt_to_string(key):
                    out += f"  string: {self._sub_opt_to_string(key)}{os.linesep}"
            out += os.linesep
        return out

    def __str__(self) -> str:
        return self._sub_opt_details()
