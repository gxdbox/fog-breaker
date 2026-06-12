from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class RawIntelligence:
    title: str
    content: str
    url: Optional[str] = None
    source_name: str = ""
    category: str = "general"
    language: Optional[str] = None
    published_at: Optional[datetime] = None


class BaseCollector(ABC):
    @abstractmethod
    def collect(self) -> List[RawIntelligence]:
        raise NotImplementedError
