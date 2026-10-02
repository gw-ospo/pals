"""Normalize candidate names from FEC and scorecard sources."""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

HONORIFICS = {"mr", "mrs", "ms", "dr", "hon", "rev", "phd", "md", "esq", "sen", "rep"}
SUFFIXES = {"jr", "sr", "ii", "iii", "iv", "v"}


@dataclass(frozen=True)
class Name:
    last: str
    first: str
    middle: tuple[str, ...]
    suffix: str
    # Alternative surnames for sources that do not mark where the surname begins
    # ("Debbie Wasserman Schultz" -> wassermanschultz, schultz).
    last_variants: tuple[str, ...] = ()

    @property
    def key(self) -> str:
        return f"{self.last}|{self.first}"


def _fold(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().replace("'", "").replace("’", "")
    text = re.sub(r"[^a-z\s-]", " ", text).replace("-", "")
    return re.sub(r"\s+", " ", text).strip()


def _tokens(text: str) -> tuple[list[str], str]:
    toks, suffix = [], ""
    for tok in _fold(text).split():
        if tok in HONORIFICS:
            continue
        if tok in SUFFIXES:
            suffix = tok
            continue
        toks.append(tok)
    return toks, suffix


def parse_fec_name(raw: str | None) -> Name:
    """`"MCBATH, LUCIA KAY MS."` -> last=mcbath, first=lucia, middle=(kay,)."""
    if not isinstance(raw, str) or not raw.strip():
        return Name("", "", (), "")
    last_part, _, rest = raw.partition(",")
    last_toks, suf1 = _tokens(last_part)
    rest_toks, suf2 = _tokens(rest)
    # Hyphenated/compound last names are kept joined so they compare equal
    # regardless of hyphenation.
    return Name(
        last="".join(last_toks),
        first=rest_toks[0] if rest_toks else "",
        middle=tuple(rest_toks[1:]),
        suffix=suf2 or suf1,
    )


def parse_scorecard_name(raw: str | None) -> Name:
    """`"Katie Britt"` -> last=britt, first=katie."""
    if not isinstance(raw, str) or not raw.strip():
        return Name("", "", (), "")
    toks, suffix = _tokens(raw)
    if not toks:
        return Name("", "", (), suffix)
    if len(toks) == 1:
        return Name(toks[0], "", (), suffix)
    # Scorecard "First [Middle...] Last"; last token is the surname. Connectives
    # (de, van, etc.) immediately before it belong to the surname.
    particles = {"de", "del", "la", "van", "von", "der", "da", "di", "le", "mc"}
    i = len(toks) - 1
    while i > 1 and toks[i - 1] in particles:
        i -= 1
    variants = tuple("".join(toks[j:]) for j in range(1, len(toks)))
    return Name(last="".join(toks[i:]), first=toks[0], middle=tuple(toks[1:i]), suffix=suffix,
                last_variants=variants)


_DISPLAY_DROP = HONORIFICS | {"the"}


def _title_token(tok: str) -> str:
    if tok in SUFFIXES and tok in {"ii", "iii", "iv", "v"}:
        return tok.upper()
    if tok in SUFFIXES:
        return tok.capitalize() + "."
    word = tok.capitalize()
    word = re.sub(r"^(Mc|Mac(?=[a-z]{4}))([a-z])", lambda m: m.group(1) + m.group(2).upper(), word)
    return re.sub(r"([-'])([a-z])", lambda m: m.group(1) + m.group(2).upper(), word)


def display_name(raw: str | None) -> str:
    """`"CORNYN, JOHN SEN. III"` -> `"John Cornyn III"`; `"MCBATH, LUCIA KAY MS."` -> `"Lucia Kay McBath"`."""
    if not isinstance(raw, str) or not raw.strip():
        return ""
    last, _, rest = raw.partition(",")
    suffix, words = "", []
    for tok in rest.split() + last.split():
        bare = re.sub(r"[^a-z]", "", tok.lower())
        if bare in _DISPLAY_DROP:
            continue
        if bare in SUFFIXES:
            suffix = bare
        elif len(bare) == 1:
            words.append(bare.upper() + ".")
        else:
            words.append(_title_token(tok.lower().rstrip(".")))
    name = " ".join(words)
    return f"{name} {_title_token(suffix)}" if suffix else name
