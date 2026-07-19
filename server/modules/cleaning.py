import re
import hashlib
from difflib import SequenceMatcher

PII_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "phone": re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
}

NOISE_LINE_PATTERNS = [
    re.compile(r"^(home|about|contact|privacy policy|terms of service|©|all rights reserved|cookie)", re.I),
    re.compile(r"^\s*$"),
]


def detect_pii(text: str) -> dict:
    findings = {}
    for label, pattern in PII_PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            findings[label] = len(matches)
    return findings


def mask_pii(text: str) -> str:
    masked = PII_PATTERNS["email"].sub("[EMAIL_REDACTED]", text)
    masked = PII_PATTERNS["phone"].sub("[PHONE_REDACTED]", masked)
    return masked


def strip_noise_lines(text: str) -> str:
    lines = text.split("\n")
    kept = [ln for ln in lines if not any(p.match(ln.strip()) for p in NOISE_LINE_PATTERNS)]
    return "\n".join(kept)


def normalize_whitespace(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def content_hash(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    return hashlib.sha256(normalized.encode()).hexdigest()


def is_near_duplicate(text: str, existing_texts: list, threshold: float = 0.90) -> bool:
    return any(SequenceMatcher(None, text, existing).ratio() > threshold for existing in existing_texts)


def clean_text(raw_text: str, mask: bool = True) -> dict:
    """Full cleaning pipeline for one scraped/parsed document."""
    text = strip_noise_lines(raw_text)
    text = normalize_whitespace(text)
    pii_found = detect_pii(text)
    if mask and pii_found:
        text = mask_pii(text)
    return {"content": text, "pii_detected": bool(pii_found), "pii_types": list(pii_found.keys())}
