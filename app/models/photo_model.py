from dataclasses import dataclass
from datetime import datetime

@dataclass
class Photo:
    """Model untuk Photo"""
    id: int
    user_id: int
    filename: str
    filepath: str
    width: int
    height: int
    created_at: str

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "filepath": self.filepath,
            "width": self.width,
            "height": self.height,
            "created_at": self.created_at
        }
