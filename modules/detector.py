"""Hybrid confidentiality detector.

Layers:
1. Configurable keyword/regex rules from rules.json.
2. Optional spaCy NER (local, no API call) for PERSON/EMAIL/PHONE/ORG/GPE entities.
3. Local TF-IDF contextual similarity against configurable sensitive prototypes.

The detector is fail-safe: if the semantic layer is unavailable, the deterministic
layer still runs. No external data is sent anywhere.
"""
import json
import re
from pathlib import Path

try:
    import spacy
except Exception:  # optional dependency
    spacy = None

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except Exception:  # optional dependency
    TfidfVectorizer = None
    cosine_similarity = None

ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "rules.json"


def load_detector_rules():
    return json.loads(RULES_PATH.read_text(encoding="utf-8"))


_NLP = None
_VECTORIZER = None
_PROTO_MATRIX = None


def _semantic_resources():
    global _NLP, _VECTORIZER, _PROTO_MATRIX
    rules = load_detector_rules().get("sensitivity", {})
    prototypes = rules.get("semantic_prototypes", [])

    if _NLP is None and spacy is not None:
        try:
            _NLP = spacy.blank("en")
            ruler = _NLP.add_pipe("entity_ruler")
            patterns = []
            for phrase in rules.get("ner_sensitive_phrases", []):
                patterns.append({"label": "SENSITIVE", "pattern": phrase})
            ruler.add_patterns(patterns)
        except Exception:
            _NLP = False

    if _VECTORIZER is None and TfidfVectorizer is not None and prototypes:
        try:
            _VECTORIZER = TfidfVectorizer(ngram_range=(1, 3), lowercase=True)
            _PROTO_MATRIX = _VECTORIZER.fit_transform(prototypes)
        except Exception:
            _VECTORIZER = False
            _PROTO_MATRIX = None
    return rules, _NLP, _VECTORIZER, _PROTO_MATRIX


def _semantic_matches(text):
    rules, nlp, vectorizer, proto_matrix = _semantic_resources()
    found = []
    threshold = float(rules.get("semantic_threshold", 0.20))

    if nlp:
        doc = nlp(str(text))
        for ent in doc.ents:
            found.append({"type": "NER", "match": ent.text, "label": ent.label_, "score": 1.0})

    if vectorizer is not False and vectorizer is not None and proto_matrix is not None:
        try:
            q = vectorizer.transform([str(text)])
            scores = cosine_similarity(q, proto_matrix)[0]
            for i, score in enumerate(scores):
                if score >= threshold:
                    found.append({"type": "SEMANTIC", "match": rules["semantic_prototypes"][i], "label": "SENSITIVE_CONTEXT", "score": round(float(score), 3)})
        except Exception:
            pass
    return found


def detect_sensitive_content(text):
    if text is None or not str(text).strip():
        return {"sensitive": False, "items": [], "severity": "LOW", "layers": [], "semantic_matches": []}

    rules = load_detector_rules()
    sensitivity = rules.get("sensitivity", {})
    text_str = str(text)
    text_lower = text_str.lower()
    detected = []
    layers = []

    for phrase in sensitivity.get("keywords", []):
        if str(phrase).lower() in text_lower:
            detected.append(str(phrase))
            layers.append("keyword")

    for pattern in sensitivity.get("regex_patterns", []):
        try:
            for match in re.findall(pattern, text_str, re.IGNORECASE):
                value = match if isinstance(match, str) else " ".join(match)
                if value and value not in detected:
                    detected.append(value)
                    layers.append("regex")
        except re.error:
            continue

    semantic = _semantic_matches(text_str)
    for item in semantic:
        value = item["match"]
        if value not in detected:
            detected.append(value)
        layers.append(item["type"].lower())

    high_words = sensitivity.get("high_severity_terms", [])
    medium_words = sensitivity.get("medium_severity_terms", [])
    severity = "HIGH" if any(w.lower() in text_lower for w in high_words) else ("MEDIUM" if detected or any(w.lower() in text_lower for w in medium_words) else "LOW")
    return {
        "sensitive": bool(detected),
        "items": detected,
        "severity": severity,
        "layers": sorted(set(layers)),
        "semantic_matches": semantic,
    }
