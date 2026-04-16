# HashedMaze
# Copyright (c) 2026 Tito de Barros Junior
# Licensed under the MIT License

from dataclasses import dataclass, asdict
@dataclass(frozen=True)
class MasterKey:
    hash: str
    salt: str

    def __post_init__(self):
        if not isinstance(self.hash, str) or \
           not isinstance(self.salt, str): \
            raise TypeError(f'Hash, and Salt must be string.')
        
        if len(self.hash) < 32:
            raise ValueError(f"The hash appears to be invalid or too short.")
        
    def to_dict(self):
        return asdict(self)