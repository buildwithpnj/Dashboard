from typing import Dict, Any, Tuple

class TaskPersistenceGuard:
    @classmethod
    def validate_write_safety(cls, payload: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates write constraints for task/goal modifications.
        Ensures:
        1. Title is not empty or filled with placeholder text.
        2. Title is at least 3 characters long to prevent junk records.
        """
        title = payload.get("title", "").strip()
        if not title:
            return False, "Task title cannot be empty."

        if len(title) < 3:
            return False, "Task title must be at least 3 characters long."

        placeholders = ["test", "placeholder", "todo", "asdf", "temp"]
        if title.lower() in placeholders:
            return False, f"Placeholder title '{title}' is not allowed for production tasks."

        # Description length check
        desc = payload.get("description", "")
        if desc and len(desc) > 1000:
            return False, "Description cannot exceed 1000 characters."

        return True, "Safe to write"
