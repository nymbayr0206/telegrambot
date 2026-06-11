from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

IMAGE_MODEL = os.environ.get("IMAGE_MODEL", "gpt-image-2").strip() or "gpt-image-2"
DEFAULT_BASE_URL = "http://GATEWAY_SERVER_IP:3010/api/gateway"
CONFIRMATION_REQUIRED = (
    os.environ.get("IMAGE_CONFIRMATION_REQUIRED", "true").strip().lower()
    not in {"0", "false", "no", "off"}
)
PENDING_STATE_FILE = Path(
    os.environ.get(
        "IMAGE_ROUTER_PENDING_FILE",
        "/opt/data/image-router-pending.json"
        if Path("/opt/data").exists()
        else "/opt/hermes-telegram-agent/data/image-router-pending.json",
    )
)
_HTTP_URL_RE = re.compile(r"https?://[^\s<>'\")\]]+")
_ASPECT_RATIO_RE = re.compile(r"\b(?:\d{1,2}\s*:\s*\d{1,2}|square|portrait|landscape)\b", re.I)
_TEXT_HINT_RE = re.compile(r"(?:text|текст|бичиг|үг)\s*[:=-]?\s*['\"“”]?([^,'\"“”]+)", re.I)
_CONFIRM_WORDS = {
    "тийм",
    "болно",
    "баталж байна",
    "үүсгэ",
    "хий",
    "ok",
    "yes",
    "go",
    "generate",
}
_CANCEL_WORDS = {
    "болих",
    "цуцал",
    "cancel",
    "stop",
}

_IMAGE_INTENT_PATTERNS = [
    re.compile(r"\b(?:create|generate|draw|make)\b.{0,80}\b(?:image|picture|photo|poster|logo|icon)\b", re.I),
    re.compile(r"\b(?:image|picture|photo|poster|logo|icon)\b.{0,40}\b(?:create|generate|draw|make)\b", re.I),
    re.compile(r"\b(?:image generate|create an image|draw|poster|logo image)\b", re.I),
    re.compile(r"(?:зураг\s*(?:үүсгэ|зур|хий|гарга)|постер\s*хий|лого\s*(?:зураг|хий|үүсгэ))", re.I),
]

_PROMPT_PREFIX_PATTERNS = [
    re.compile(r"^\s*(?:please\s+)?(?:create|generate|draw|make)\s+(?:an?\s+)?(?:image|picture|photo|poster|logo|icon)\s*(?:of|for|about)?\s*", re.I),
    re.compile(r"^\s*(?:image\s+generate|create an image|draw|poster|logo image)\s*[:,-]?\s*", re.I),
    re.compile(r"^\s*(?:зураг\s*(?:үүсгэ|зур|хий|гарга)|постер\s*хий|лого\s*(?:зураг|хий|үүсгэ))\s*[:,-]?\s*", re.I),
]


def register(ctx: Any) -> None:
    ctx.register_hook("pre_gateway_dispatch", _route_image_intent)


def _route_image_intent(event: Any, gateway: Any, **_: Any) -> dict[str, str] | None:
    if getattr(event, "internal", False):
        return None

    source = getattr(event, "source", None)
    platform = str(getattr(getattr(source, "platform", None), "value", getattr(source, "platform", ""))).lower()
    if platform != "telegram":
        return None

    text = (getattr(event, "text", "") or "").strip()
    if not text or text.startswith("/"):
        return None

    chat_id = str(getattr(source, "chat_id", "") or "")
    pending = _get_pending_request(chat_id) if chat_id else None
    if pending:
        if _is_cancel(text):
            _schedule_task(gateway, _handle_cancel_request(event, gateway))
            return {"action": "skip", "reason": "telegram_image_cancel"}
        if _is_confirmation(text):
            _schedule_task(gateway, _handle_confirmed_request(event, gateway, pending))
            return {"action": "skip", "reason": "telegram_image_confirmed"}
        _schedule_task(gateway, _handle_pending_followup(event, gateway))
        return {"action": "skip", "reason": "telegram_image_awaiting_confirmation"}

    if not _is_image_intent(text):
        return None

    if not CONFIRMATION_REQUIRED:
        _schedule_task(gateway, _handle_confirmed_request(event, gateway, {"prompt": _extract_prompt(text)}))
        return {"action": "skip", "reason": "telegram_image_intent_no_confirmation"}

    _schedule_task(gateway, _handle_new_image_request(event, gateway))
    return {"action": "skip", "reason": "telegram_image_intent"}


def _schedule_task(gateway: Any, coro: Any) -> None:
    loop = asyncio.get_running_loop()
    task = loop.create_task(coro)
    background_tasks = getattr(gateway, "_background_tasks", None)
    if isinstance(background_tasks, set):
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)


def _is_image_intent(text: str) -> bool:
    return any(pattern.search(text) for pattern in _IMAGE_INTENT_PATTERNS)


def _is_confirmation(text: str) -> bool:
    return _normalize_control_text(text) in _CONFIRM_WORDS


def _is_cancel(text: str) -> bool:
    return _normalize_control_text(text) in _CANCEL_WORDS


def _normalize_control_text(text: str) -> str:
    return re.sub(r"^[\s.!?,;:]+|[\s.!?,;:]+$", "", text.strip().lower())


def _extract_prompt(text: str) -> str:
    prompt = text.strip()
    for pattern in _PROMPT_PREFIX_PATTERNS:
        prompt = pattern.sub("", prompt).strip()
    return prompt or text.strip()


async def _handle_new_image_request(event: Any, gateway: Any) -> None:
    source = getattr(event, "source", None)
    chat_id = str(getattr(source, "chat_id", "") or "")
    if not chat_id:
        return

    adapter = _get_telegram_adapter(event, gateway)
    if adapter is None:
        logger.warning("telegram-image-router: Telegram adapter unavailable")
        return

    prompt = _extract_prompt(getattr(event, "text", "") or "")
    metadata = _telegram_metadata(source, event)
    reply_to = str(getattr(event, "message_id", "") or "") or None

    if _prompt_is_too_vague(prompt):
        await _send_text(adapter, chat_id, _clarification_message(), reply_to, metadata)
        return

    _set_pending_request(chat_id, prompt)
    await _send_text(adapter, chat_id, _confirmation_message(prompt), reply_to, metadata)


async def _handle_confirmed_request(event: Any, gateway: Any, pending: dict[str, Any]) -> None:
    source = getattr(event, "source", None)
    chat_id = str(getattr(source, "chat_id", "") or "")
    if not chat_id:
        return

    adapter = _get_telegram_adapter(event, gateway)
    if adapter is None:
        logger.warning("telegram-image-router: Telegram adapter unavailable")
        return

    metadata = _telegram_metadata(source, event)
    reply_to = str(getattr(event, "message_id", "") or "") or None
    prompt = str(pending.get("prompt") or "").strip()
    if not prompt:
        _clear_pending_request(chat_id)
        await _send_text(adapter, chat_id, _clarification_message(), reply_to, metadata)
        return

    await _send_text(adapter, chat_id, "Зураг үүсгэж эхэллээ. Түр хүлээнэ үү...", reply_to, metadata)

    try:
        image_url = await _generate_image(prompt)
    except Exception as exc:
        logger.warning("telegram-image-router: image generation failed: %s", exc)
        _clear_pending_request(chat_id)
        await _send_text(
            adapter,
            chat_id,
            "Уучлаарай, зураг үүсгэхэд алдаа гарлаа. Дараа дахин оролдоорой.",
            reply_to,
            metadata,
        )
        return

    _clear_pending_request(chat_id)
    caption = "Generated image"
    try:
        result = await adapter.send_image(
            chat_id=chat_id,
            image_url=image_url,
            caption=caption,
            reply_to=reply_to,
            metadata=metadata,
        )
        if not getattr(result, "success", False):
            await _send_text(adapter, chat_id, image_url, reply_to, metadata)
    except Exception as exc:
        logger.warning("telegram-image-router: Telegram photo send failed: %s", exc)
        await _send_text(adapter, chat_id, image_url, reply_to, metadata)


async def _handle_cancel_request(event: Any, gateway: Any) -> None:
    source = getattr(event, "source", None)
    chat_id = str(getattr(source, "chat_id", "") or "")
    if not chat_id:
        return
    adapter = _get_telegram_adapter(event, gateway)
    if adapter is None:
        logger.warning("telegram-image-router: Telegram adapter unavailable")
        return
    _clear_pending_request(chat_id)
    metadata = _telegram_metadata(source, event)
    reply_to = str(getattr(event, "message_id", "") or "") or None
    await _send_text(adapter, chat_id, "Зураг үүсгэх хүсэлтийг цуцаллаа.", reply_to, metadata)


async def _handle_pending_followup(event: Any, gateway: Any) -> None:
    source = getattr(event, "source", None)
    chat_id = str(getattr(source, "chat_id", "") or "")
    if not chat_id:
        return
    adapter = _get_telegram_adapter(event, gateway)
    if adapter is None:
        logger.warning("telegram-image-router: Telegram adapter unavailable")
        return
    metadata = _telegram_metadata(source, event)
    reply_to = str(getattr(event, "message_id", "") or "") or None
    await _send_text(
        adapter,
        chat_id,
        "Зураг үүсгэхийг батлах бол 'тийм', цуцлах бол 'болих' гэж бичээрэй.",
        reply_to,
        metadata,
    )


def _get_telegram_adapter(event: Any, gateway: Any) -> Any:
    source = getattr(event, "source", None)
    adapters = getattr(gateway, "adapters", None)
    if isinstance(adapters, dict):
        return adapters.get(getattr(source, "platform", None))
    return None


def _telegram_metadata(source: Any, event: Any) -> dict[str, Any] | None:
    thread_id = getattr(source, "thread_id", None)
    if thread_id is None:
        return None
    metadata: dict[str, Any] = {"thread_id": str(thread_id)}
    if getattr(source, "chat_type", None) == "dm":
        metadata["telegram_dm_topic_reply_fallback"] = True
        tid = str(thread_id)
        if tid and tid != "1":
            metadata["direct_messages_topic_id"] = tid
        message_id = getattr(event, "message_id", None)
        if message_id is not None:
            metadata["telegram_reply_to_message_id"] = str(message_id)
    return metadata


def _prompt_is_too_vague(prompt: str) -> bool:
    normalized = prompt.strip().lower()
    if not normalized:
        return True
    reduced = re.sub(
        r"\b(?:poster|image|picture|photo|logo|icon|зураг|постер|лого|create|generate|draw|make|хий|үүсгэ|зур|гарга)\b",
        " ",
        normalized,
        flags=re.I,
    )
    meaningful_tokens = re.findall(r"[\w\u0400-\u04ff]+", reduced)
    return len(meaningful_tokens) < 3 and not _ASPECT_RATIO_RE.search(normalized)


def _clarification_message() -> str:
    return "Ямар poster хийх вэ? Сэдэв, оруулах текст, өнгө/style, харьцааг хэлээрэй."


def _confirmation_message(prompt: str) -> str:
    summary = _summarize_prompt(prompt)
    return (
        "Дараах зураг үүсгэх үү?\n"
        f"Сэдэв: {summary['subject']}\n"
        f"Style: {summary['style']}\n"
        f"Background/өнгө: {summary['color']}\n"
        f"Харьцаа: {summary['aspect_ratio']}\n"
        f"Оруулах текст: {summary['text']}\n"
        "Батлах бол 'тийм' гэж бичээрэй. Цуцлах бол 'болих' гэж бичээрэй."
    )


def _summarize_prompt(prompt: str) -> dict[str, str]:
    style_matches = re.findall(
        r"\b(?:modern|minimal|minimalist|realistic|cinematic|flat|vector|3d)\b",
        prompt,
        flags=re.I,
    )
    color_matches = re.findall(
        r"\b(?:white|black|red|blue|green|yellow|purple|orange|dark|light|bright|pastel|moody)\b|"
        r"(?:цагаан|хар|улаан|цэнхэр|ногоон|шар|нил ягаан|улбар|гэрэлтэй|бараан)",
        prompt,
        flags=re.I,
    )
    ratio_match = _ASPECT_RATIO_RE.search(prompt)
    text_match = _TEXT_HINT_RE.search(prompt)

    subject = prompt
    for token in style_matches + color_matches:
        subject = re.sub(re.escape(token), " ", subject, flags=re.I)
    subject = _ASPECT_RATIO_RE.sub(" ", subject)
    subject = re.sub(r"\b(?:poster|image|picture|photo|logo|icon|зураг|постер|лого)\b", " ", subject, flags=re.I)
    subject = re.sub(r"[,;:]+", " ", subject)
    subject = re.sub(r"\s+", " ", subject).strip()

    return {
        "subject": subject or prompt.strip(),
        "style": ", ".join(dict.fromkeys(style_matches)) if style_matches else "тодорхойгүй",
        "color": ", ".join(dict.fromkeys(color_matches)) if color_matches else "тодорхойгүй",
        "aspect_ratio": ratio_match.group(0).replace(" ", "") if ratio_match else "1:1",
        "text": text_match.group(1).strip() if text_match else "байхгүй",
    }


def _load_pending_requests() -> dict[str, dict[str, Any]]:
    try:
        with PENDING_STATE_FILE.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        return {}
    except Exception as exc:
        logger.warning("telegram-image-router: failed to read pending state: %s", exc)
        return {}
    if not isinstance(data, dict):
        return {}
    return {str(key): value for key, value in data.items() if isinstance(value, dict)}


def _save_pending_requests(data: dict[str, dict[str, Any]]) -> None:
    PENDING_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp_path = PENDING_STATE_FILE.with_suffix(PENDING_STATE_FILE.suffix + ".tmp")
    with temp_path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(temp_path, PENDING_STATE_FILE)


def _get_pending_request(chat_id: str) -> dict[str, Any] | None:
    if not chat_id:
        return None
    pending = _load_pending_requests().get(chat_id)
    if isinstance(pending, dict) and pending.get("status") == "awaiting_confirmation":
        return pending
    return None


def _set_pending_request(chat_id: str, prompt: str) -> None:
    pending = _load_pending_requests()
    pending[chat_id] = {
        "prompt": prompt,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "awaiting_confirmation",
    }
    _save_pending_requests(pending)


def _clear_pending_request(chat_id: str) -> None:
    pending = _load_pending_requests()
    if chat_id in pending:
        del pending[chat_id]
        _save_pending_requests(pending)


async def _generate_image(prompt: str) -> str:
    import httpx

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing")

    base_url = os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    payload = {
        "model": IMAGE_MODEL,
        "prompt": prompt,
        "parameters": {"aspect_ratio": "1:1"},
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{base_url}/generate",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

    try:
        data = response.json()
    except Exception:
        data = None

    if response.status_code >= 400:
        message = _extract_error_message(data) or f"HTTP {response.status_code}"
        raise RuntimeError(message)

    logger.debug("telegram-image-router: gateway response shape: %s", _response_shape(data))

    image_url, image_path = _find_image_url(data)
    if not image_url:
        raise RuntimeError("gateway response did not include an image URL")
    logger.debug("telegram-image-router: extracted image URL from %s", image_path)
    return image_url


def _extract_error_message(data: Any) -> str:
    if isinstance(data, dict):
        error = data.get("error")
        if isinstance(error, dict):
            message = error.get("message")
            if isinstance(message, str):
                return message[:300]
        message = data.get("message")
        if isinstance(message, str):
            return message[:300]
    return ""


def _find_image_url(data: Any) -> tuple[str, str]:
    if isinstance(data, dict):
        explicit_paths = (
            ("data.provider.result_urls[0]", ("data", "provider", "result_urls", 0), False),
            ("data.provider.images[0]", ("data", "provider", "images", 0), False),
            ("data.provider.output", ("data", "provider", "output"), True),
            ("data.provider.data.result_urls[0]", ("data", "provider", "data", "result_urls", 0), False),
            ("data.provider.data.images[0]", ("data", "provider", "data", "images", 0), False),
            ("provider.result_urls[0]", ("provider", "result_urls", 0), False),
            ("provider.images[0]", ("provider", "images", 0), False),
            ("image_url", ("image_url",), False),
            ("url", ("url",), False),
        )
        for path_name, path, extract_from_text in explicit_paths:
            value = _get_path(data, path)
            found = _url_from_value(value, extract_from_text=extract_from_text)
            if found:
                return found, path_name

        preferred_keys = (
            "image_url",
            "url",
            "output_url",
            "result_url",
            "asset_url",
            "download_url",
        )
        for key in preferred_keys:
            value = data.get(key)
            found = _url_from_value(value)
            if found:
                return found, key
        for value in data.values():
            found, path = _find_image_url(value)
            if found:
                return found, path
    elif isinstance(data, list):
        for item in data:
            found, path = _find_image_url(item)
            if found:
                return found, path
    return "", ""


def _get_path(data: Any, path: tuple[str | int, ...]) -> Any:
    current = data
    for part in path:
        if isinstance(part, str):
            if not isinstance(current, dict) or part not in current:
                return None
            current = current[part]
        elif isinstance(part, int):
            if not isinstance(current, list) or len(current) <= part:
                return None
            current = current[part]
    return current


def _url_from_value(value: Any, *, extract_from_text: bool = False) -> str:
    if isinstance(value, str):
        if value.startswith(("http://", "https://")):
            return value
        if extract_from_text:
            match = _HTTP_URL_RE.search(value)
            if match:
                return match.group(0)
    elif isinstance(value, dict):
        for key in ("url", "image_url", "output_url", "result_url", "asset_url", "download_url"):
            found = _url_from_value(value.get(key))
            if found:
                return found
    return ""


def _response_shape(data: Any, depth: int = 0) -> Any:
    if depth >= 4:
        return type(data).__name__
    if isinstance(data, dict):
        return {
            str(key): _response_shape(value, depth + 1)
            for key, value in data.items()
            if str(key).lower() not in {"authorization", "api_key", "apikey", "token", "access_token"}
        }
    if isinstance(data, list):
        if not data:
            return []
        return [_response_shape(data[0], depth + 1)]
    return type(data).__name__


async def _send_text(adapter: Any, chat_id: str, content: str, reply_to: str | None, metadata: dict[str, Any] | None) -> None:
    await adapter.send(chat_id=chat_id, content=content, reply_to=reply_to, metadata=metadata)
