import dataclasses
import json
from typing import List

from models import Match


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


def encode_matches(matches: List[Match]) -> str:
    return json.dumps(matches, cls=JSONEncoder)


def decode_matches(raw_json: str) -> List[Match]:
    parsed = json.loads(raw_json)
    return [Match.from_dict(d) for d in parsed]
