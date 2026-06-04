"""workshop_bench/governance/core/schema.py — Pydantic-style schema for patch operations."""


class PatchOperation:
    """Validates a single patch operation dict returned by Gemini."""

    VALID_OPS = {"replace", "insert_after", "delete"}

    def __init__(self, **kwargs):
        filename = kwargs.get("filename", "")
        operation = kwargs.get("operation", "")
        if not filename:
            raise ValueError("PatchOperation requires a non-empty 'filename' field.")
        if operation not in self.VALID_OPS:
            raise ValueError(
                f"PatchOperation: invalid operation '{operation}'. "
                f"Must be one of {self.VALID_OPS}."
            )
        self.filename = filename
        self.operation = operation
        self.old = kwargs.get("old", "")
        self.new = kwargs.get("new", "")
        self.anchor = kwargs.get("anchor", "")

    def __repr__(self):
        return f"PatchOperation(op={self.operation!r}, file={self.filename!r})"
