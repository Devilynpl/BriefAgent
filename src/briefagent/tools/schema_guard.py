from typing import Any, Dict, Optional
from pydantic import BaseModel, ValidationError


class ToolError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def validate_tool_input(schema_cls: type[BaseModel], input_data: Dict[str, Any]) -> BaseModel:
    """
    Schema Guard: Validates arguments passed to a tool against its Pydantic model.
    If invalid, raises structured ToolError with clean feedback for agent self-correction.
    """
    try:
        return schema_cls.model_validate(input_data)
    except ValidationError as err:
        errors = err.errors()
        error_msgs = []
        for e in errors:
            loc = ".".join(str(l) for l in e.get("loc", []))
            msg = e.get("msg", "Invalid argument")
            error_msgs.append(f"Field '{loc}': {msg}")
        raise ToolError(f"ToolError: Invalid argument(s). {'; '.join(error_msgs)}")
