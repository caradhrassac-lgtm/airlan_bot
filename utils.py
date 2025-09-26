import datetime as dt, urllib.parse

KW_HVAC = ["hvac", "agua helada", "chilled water", "chiller", "fan coil", "ahu", "torre de enfriamiento"]
KW_TENDER = ["licitación", "licitacion", "concurso", "rfp", "rfq", "tender", "procurement", "convocatoria", "seace"]

def now_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def normalize_url(u: str) -> str:
    try:
        p = urllib.parse.urlsplit(u.strip())
        q = urllib.parse.parse_qsl(p.query, keep_blank_values=True)
        q = [(k, v) for (k, v) in q if not k.lower().startswith(("utm_", "fbclid", "gclid"))]
        return urllib.parse.urlunsplit((p.scheme, p.netloc.lower(), p.path, urllib.parse.urlencode(q), ""))
    except Exception:
        return u.strip()

def domain_of(u: str) -> str:
    try:
        return urllib.parse.urlsplit(u).netloc.lower()
    except Exception:
        return ""

def relevance_score(title: str, snippet: str) -> int:
    text = f"{title} {snippet}".lower()
    score = 0
    for kw in KW_HVAC:
        if kw in text:
            score += 3
    for kw in KW_TENDER:
        if kw in text:
            score += 2
    return score
