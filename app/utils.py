import datetime
import json
from typing import Any, Dict, Iterable, Optional

from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError

def current_timestamp() -> str:
    return datetime.datetime.utcnow().isoformat()

def parse_iso_datetime(value: str) -> datetime.datetime:
    try:
        return datetime.datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Invalid ISO datetime string: {value}") from exc

def serialize_obj(obj: Any) -> Dict[str, Any]:
    if hasattr(obj, "dict"):
        return obj.dict()
    return jsonable_encoder(obj)

def safe_json_dump(data: Any) -> str:
    try:
        return json.dumps(serialize_obj(data), default=str)
    except Exception as exc:
        raise ValueError("Failed to serialize data to JSON") from exc

def validate_and_encode(
    schema_cls, payload: Dict[str, Any]
) -> Dict[str, Any]:
    try:
        obj = schema_cls(**payload)
    except ValidationError as exc:
        raise ValueError(f"Schema validation error: {exc}") from exc
    return serialize_obj(obj)

def build_response(
    data: Optional[Any] = None,
    message: str = "Success",
    status_code: int = 200,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"status": status_code, "message": message}
    if data is not None:
        payload["data"] = serialize_obj(data)
    return payload

def iterate_chunks(iterable: Iterable[Any], chunk_size: int = 1000) -> Iterable[list]:
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= chunk_size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk

def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {}
    for d in dicts:
        merged.update(d)
    return merged

def safe_get(dic: Dict[Any, Any], key: Any, default: Any = None) -> Any:
    try:
        return dic[key]
    except KeyError:
        return default

def ensure_str(value: Any) -> str:
    if isinstance(value, str):
        return value
    raise TypeError(f"Expected string, got {type(value).__name__}")

def list_to_set(items: Iterable[Any]) -> set:
    return set(items)

def dict_from_items(items: Iterable[tuple]) -> Dict[Any, Any]:
    result: Dict[Any, Any] = {}
    for key, value in items:
        result[key] = value
    return result

def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def filter_none(d: Dict[Any, Any]) -> Dict[Any, Any]:
    return {k: v for k, v in d.items() if v is not None}

def ensure_list_of_dicts(data: Any) -> list:
    if isinstance(data, list):
        return data
    raise TypeError("Expected a list of dictionaries")

def truncate_string(s: str, max_length: int = 255) -> str:
    return s[:max_length] if len(s) > max_length else s

def safe_round(value: Any, ndigits: int = 2) -> float:
    try:
        return round(float(value), ndigits)
    except (TypeError, ValueError):
        return 0.0

def json_response(data: Any, status_code: int = 200) -> Dict[str, Any]:
    return {"status": status_code, "data": serialize_obj(data)}

def merge_lists(*lists: Iterable[Any]) -> list:
    result: list = []
    for lst in lists:
        result.extend(lst)
    return result

def dedupe_list(items: Iterable[Any]) -> list:
    seen = set()
    unique: list = []
    for item in items:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique

def ensure_positive_int(value: Any, default: int = 1) -> int:
    try:
        iv = int(value)
        return iv if iv > 0 else default
    except (TypeError, ValueError):
        return default

def get_env_var(name: str, default: Optional[str] = None) -> str:
    import os
    return os.getenv(name, default or "")

def format_datetime(dt: datetime.datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    return dt.strftime(fmt)