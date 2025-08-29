from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass
class Message:
    conversation_id: int
    role: str
    message_text: str
    model_version: str
    message_order: int
    conversational: str
    code: str
    other: str
    code_blocks: Optional[List[Dict[str, str]]]