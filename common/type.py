from __future__ import annotations

import dataclasses
import json

@dataclasses.dataclass
class Payload:
    timestamp: float
    message: str

    @staticmethod
    def loads(raw: str | bytes | bytearray) -> Payload:
        dd = json.loads(raw)
        return Payload(dd['timestamp'], dd['message'])

    def encode(self) -> str:
        return json.dumps(dataclasses.asdict(self))
