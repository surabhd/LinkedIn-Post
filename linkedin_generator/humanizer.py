"""
humanizer.py
------------
Post-processing scrubber that removes AI slop patterns from generated text.
Operates via regex substitution and token-level filtering.
No external dependencies beyond the standard library.
"""

import re
from typing import List, Tuple

# ── 1. Direct word/phrase substitutions ──────────────────────────────────────
# (pattern, replacement) — applied in order, case-insensitive
SUBSTITUTIONS: List[Tuple[str, str]] = [
    # Hollow openers
    (r"\bIn today's fast[- ]paced (world|environment|business world)\b[,.]?\s*", ""),
    (r"\bIn (the |an )?ever[- ]evolving\b[^,.]*, ?", ""),
    (r"\bAs we navigate\b[^,.]*, ?", ""),
    (r"\bIn an era where\b[^,.]*, ?", ""),
    (r"\bNow more than ever[,.]?\s*", ""),
    (r"\bMore than ever before[,.]?\s*", ""),
    (r"\bIn today's digital age[,.]?\s*", ""),
    (r"\bIn today's business landscape[,.]?\s*", ""),
    (r"\bIn today's world[,.]?\s*", ""),
    (r"\bIt's (important|worth) (to note|noting) that\b[,]?\s*", ""),
    (r"\bThat being said[,.]?\s*", ""),
    (r"\bHaving said that[,.]?\s*", ""),
    (r"\bAt the end of the day[,.]?\s*", ""),
    (r"\bThe bottom line is[,:]?\s*", ""),
    (r"\bIn conclusion[,.]?\s*", ""),
    (r"\bIn summary[,.]?\s*", ""),
    (r"\bTo sum (up|it up)[,.]?\s*", ""),
    (r"\bThis is why[,:]?\s*", ""),
    (r"\bP\.S\..*", ""),  # Strip P.S. tails entirely

    # Buzzword replacements with plain English
    (r"\bleverag(e|ing|ed)\b", "use"),
    (r"\bdelv(e|ing)\b", "look"),
    (r"\bgame[- ]chang(er|ing)\b", "significant shift"),
    (r"\bparadigm shift\b", "fundamental change"),
    (r"\bsynerg(y|ies)\b", "coordination"),
    (r"\bholistic\b", "end-to-end"),
    (r"\brobust\b", "strong"),
    (r"\bseamless(ly)?\b", "smooth"),
    (r"\btransformative\b", "significant"),
    (r"\bgroundbreaking\b", "notable"),
    (r"\bcutting[- ]edge\b", "modern"),
    (r"\bunlock(s|ing|ed)?\b", "open up"),
    (r"\bempower(s|ing|ed|ment)?\b", "enable"),
    (r"\bscal(able|ability|e)\b", "able to grow"),
    (r"\breimagi(ne|nes|ned|ning)\b", "rethink"),
    (r"\bdisrupt(s|ive|ion|ed)?\b", "change"),
    (r"\bharness(es|ed|ing)?\b", "use"),
    (r"\bspearhead(s|ed|ing)?\b", "lead"),
    (r"\bfoster(s|ed|ing)?\b", "build"),
    (r"\bcatalyst\b", "driver"),
    (r"\bpivotal\b", "critical"),
    (r"\bunprecedented\b", "new"),
    (r"\bnavigate the\b", "deal with the"),
    (r"\becosystem\b", "environment"),
    (r"\blandscape\b", "space"),
    (r"\bstreamlin(e|ing)\b", "simplify"),
    (r"\bmove the needle\b", "make progress"),
    (r"\blow[- ]hanging fruit\b", "easy wins"),
    (r"\bcircle back\b", "follow up"),
    (r"\bdeep[ -]dive\b", "closer look"),
    (r"\bget buy-in\b", "get support"),
    (r"\bsynergize\b", "work together"),
    (r"\bideate\b", "brainstorm"),
    (r"\bsolutioning\b", "solving"),
    (r"\bboil the ocean\b", "try to do everything"),
]

# ── 2. Patterns to remove entirely (matched lines/phrases) ───────────────────
REMOVE_PATTERNS: List[str] = [
    r"^Picture this[:\-].*",                   # "Picture this:" openers
    r"^Imagine[:\-].*",                        # "Imagine:" openers
    r".*hashtag.*\d.*",                        # weird hashtag text
]

# ── 3. Fabricated stat detector — flag for removal/softening ─────────────────
STAT_PATTERN = re.compile(
    r"\b\d{1,3}%\s*(faster|cheaper|reduction|improvement|increase|more|less|better|cost)\b"
    r"|\b\$[\d,]+[MBK]?\s*(annually|per year|in savings|in revenue|in losses)\b"
    r"|\b(achieve|saw|realized|reported|showed)\s+\d{1,3}%\b",
    re.IGNORECASE,
)


def _apply_substitutions(text: str) -> str:
    for pattern, replacement in SUBSTITUTIONS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def _remove_patterns(text: str) -> str:
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        skip = False
        for pat in REMOVE_PATTERNS:
            if re.match(pat, line.strip(), flags=re.IGNORECASE):
                skip = True
                break
        if not skip:
            cleaned.append(line)
    return "\n".join(cleaned)


def _soften_fake_stats(text: str) -> str:
    """Replace fabricated numeric claims with qualitative language."""
    replacements = [
        (r"\b\d{1,3}%\s*faster\b", "significantly faster"),
        (r"\b\d{1,3}%\s*reduction\b", "notable reduction"),
        (r"\b\d{1,3}%\s*(improvement|increase)\b", "meaningful improvement"),
        (r"\b\d{1,3}%\s*cheaper\b", "considerably less expensive"),
        (r"\b\d{1,3}%\s*(more|better)\b", "considerably more"),
        (r"\b\d{1,3}%\s*(less)\b", "considerably less"),
        (r"\b\$[\d,]+[MBK]?\s*(annually|per year|in savings|in revenue|in losses)\b",
         "significant financial impact"),
    ]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def _fix_whitespace(text: str) -> str:
    """Clean up double spaces and leading/trailing whitespace per line."""
    lines = text.split("\n")
    lines = [re.sub(r"  +", " ", line).strip() for line in lines]
    # Collapse more than 2 consecutive blank lines
    result = re.sub(r"\n{3,}", "\n\n", "\n".join(lines))
    return result.strip()


def _strip_double_hashtags(text: str) -> str:
    """Remove duplicate hashtag blocks if the model repeats them."""
    seen = set()
    words = text.split()
    output = []
    for word in words:
        if word.startswith("#"):
            if word.lower() in seen:
                continue
            seen.add(word.lower())
        output.append(word)
    return " ".join(output)


def humanize(text: str) -> str:
    """
    Main entry point. Apply all humanization passes to a generated post.
    Returns a cleaned, more human-sounding version of the text.
    """
    text = _apply_substitutions(text)
    text = _remove_patterns(text)
    text = _soften_fake_stats(text)
    text = _fix_whitespace(text)
    text = _strip_double_hashtags(text)
    return text
