"""AI preference ranking and explanation service using Groq API with robust deterministic fallback."""
import os
import json
import re
from typing import List, Dict, Any, Tuple, Optional
from dotenv import load_dotenv

load_dotenv()

# Primary and fallback Groq models
PRIMARY_MODEL = "llama-3.3-70b-versatile"
FALLBACK_MODEL = "llama-3.1-8b-instant"


def _get_groq_client(api_key: Optional[str] = None):
    """Initializes Groq client if API key is provided or found in environment."""
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        # Check Streamlit secrets if available
        try:
            import streamlit as st
            if "GROQ_API_KEY" in st.secrets:
                key = st.secrets["GROQ_API_KEY"]
        except Exception:
            pass

    if not key or not key.strip() or key.strip() == "your_groq_api_key_here":
        return None

    try:
        from groq import Groq
        return Groq(api_key=key.strip())
    except Exception as exc:
        print(f"[AI Service] Groq client initialization failed: {exc}")
        return None


def rank_places(
    places: List[Dict[str, Any]],
    preferences: Dict[str, Any],
    api_key: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], bool, str]:
    """
    Ranks candidate places based on user preferences.
    Uses Groq LLM if configured; otherwise uses intelligent deterministic scoring.

    Returns:
        (ranked_places, used_llm: bool, explanation_or_notice: str)
    """
    if not places:
        return [], False, "No nearby places found to rank."

    client = _get_groq_client(api_key)
    if client:
        try:
            ranked, note = _llm_rank_places(client, places, preferences)
            return ranked, True, note
        except Exception as exc:
            print(f"[AI Service] LLM ranking call failed, using deterministic ranking: {exc}")

    # Deterministic fallback
    ranked = _deterministic_rank_places(places, preferences)
    notice = "AI ranking unavailable (no Groq API key configured) — showing best matches using place categories and tags."
    return ranked, False, notice


def generate_ai_explanation(
    fair_point: Dict[str, Any],
    travel_data: List[Dict[str, Any]],
    fairness_metrics: Dict[str, Any],
    api_key: Optional[str] = None,
) -> str:
    """
    Generates a concise, human-readable justification for the chosen meeting point.
    """
    client = _get_groq_client(api_key)
    if client:
        try:
            prompt = (
                f"MeetSpot calculated a meeting point at: {fair_point.get('name', 'Fair Point')} "
                f"({fair_point.get('address', '')}).\n"
                f"Participant journeys:\n"
                + "\n".join(f"- {p['name']}: {p['time_min']:.0f} mins ({p.get('distance_km', 0):.1f} km)" for p in travel_data)
                + f"\nMetrics: Longest={fairness_metrics.get('max_time_min', 0):.0f}m, "
                f"Shortest={fairness_metrics.get('min_time_min', 0):.0f}m, "
                f"Difference gap={fairness_metrics.get('gap_min', 0):.0f}m, "
                f"Average={fairness_metrics.get('avg_time_min', 0):.1f}m.\n"
                "In 2 natural, friendly sentences, explain to the group why this is the fairest meeting point "
                "based on equalized travel times rather than just raw midpoint distance."
            )
            resp = client.chat.completions.create(
                model=PRIMARY_MODEL,
                messages=[
                    {"role": "system", "content": "You are MeetSpot's AI fairness coordinator. Be concise, warm, and precise with numbers."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.6,
                max_tokens=150,
            )
            content = resp.choices[0].message.content
            if content:
                return content.strip()
        except Exception as exc:
            print(f"[AI Service] LLM explanation failed: {exc}")

    # Deterministic fallback explanation
    gap = fairness_metrics.get("gap_min", 0)
    max_t = fairness_metrics.get("max_time_min", 0)
    min_t = fairness_metrics.get("min_time_min", 0)
    avg_t = fairness_metrics.get("avg_time_min", 0)

    if gap <= 3:
        balance_desc = "virtually identical travel times"
    elif gap <= 7:
        balance_desc = "a well-balanced travel split"
    else:
        balance_desc = "the minimum possible travel spread"

    return (
        f"MeetSpot selected this location because it delivers {balance_desc} across all members. "
        f"The longest journey is approximately {max_t:.0f} minutes and the shortest is {min_t:.0f} minutes — "
        f"keeping everyone within a {gap:.0f}-minute window with an average commute of {avg_t:.0f} minutes."
    )


def _llm_rank_places(
    client,
    places: List[Dict[str, Any]],
    preferences: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], str]:
    """Calls Groq to interpret preferences and rank candidate venues."""
    simplified_places = []
    for idx, p in enumerate(places):
        simplified_places.append({
            "index": idx,
            "name": p.get("name"),
            "category": p.get("category"),
            "distance_m": p.get("distance_meters"),
            "cuisine": p.get("cuisine"),
            "outdoor": p.get("outdoor_seating"),
        })

    prompt = f"""
Given the following user meetup preferences:
- Preferred Cuisine: {preferences.get('cuisine', 'Any')}
- Preferred Atmosphere: {preferences.get('atmosphere', 'Any')}
- Preferred Budget: {preferences.get('budget', 'Any')}
- Free-text request: "{preferences.get('freetext', '')}"

Rank these {len(simplified_places)} candidate places from best to worst match:
{json.dumps(simplified_places, indent=2)}

Respond with ONLY valid JSON containing a single array of objects with keys:
"index": (integer matching candidate index),
"match_score": (integer 50-99 representing compatibility percentage),
"reason": (one punchy sentence explaining why this fits the user's preference).
"""
    response = client.chat.completions.create(
        model=PRIMARY_MODEL,
        messages=[
            {"role": "system", "content": "You are a venue curation assistant. Return ONLY a valid JSON array."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        max_tokens=600,
    )

    raw_text = response.choices[0].message.content.strip()

    # Extract JSON array
    json_match = re.search(r"\[.*\]", raw_text, re.DOTALL)
    if not json_match:
        raise ValueError("Could not find JSON array in LLM response")

    rankings = json.loads(json_match.group(0))

    ranked_results = []
    seen_indices = set()
    for item in rankings:
        idx = item.get("index")
        if idx is not None and 0 <= idx < len(places) and idx not in seen_indices:
            p = dict(places[idx])
            p["match_score"] = item.get("match_score", 85)
            p["reason"] = item.get("reason", "Good match based on group preferences.")
            ranked_results.append(p)
            seen_indices.add(idx)

    # Append any remaining places not returned by LLM
    for idx, p in enumerate(places):
        if idx not in seen_indices:
            fallback_p = dict(p)
            fallback_p["match_score"] = 70
            fallback_p["reason"] = "Nearby alternative venue."
            ranked_results.append(fallback_p)

    return ranked_results, "Places ranked by Groq AI according to group preferences."


def _deterministic_rank_places(
    places: List[Dict[str, Any]],
    preferences: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Calculates deterministic heuristic match scores for candidate venues."""
    pref_cuisine = str(preferences.get("cuisine", "")).lower()
    pref_atmo = str(preferences.get("atmosphere", "")).lower()
    pref_budget = str(preferences.get("budget", "")).lower()
    pref_free = str(preferences.get("freetext", "")).lower()

    scored = []
    for p in places:
        score = 70  # Base score
        reasons = []

        cat = p.get("category", "").lower()
        cuisine = p.get("cuisine", "").lower()
        tags_str = str(p.get("tags", {})).lower()
        name = p.get("name", "").lower()

        # Cuisine matching
        if pref_cuisine and pref_cuisine != "any":
            if pref_cuisine in cuisine or pref_cuisine in tags_str or pref_cuisine in name:
                score += 15
                reasons.append(f"offers {pref_cuisine} cuisine")

        # Atmosphere matching
        if "outdoor" in pref_atmo or "outdoor" in pref_free:
            if p.get("outdoor_seating") == "yes" or "outdoor" in tags_str:
                score += 10
                reasons.append("has outdoor seating")

        if "quiet" in pref_atmo or "quiet" in pref_free:
            if cat == "cafe" or "cafe" in name:
                score += 8
                reasons.append("cafe atmosphere suitable for conversation")

        if "family" in pref_atmo or "family" in pref_free:
            if cat == "restaurant":
                score += 6
                reasons.append("spacious restaurant setting")

        # Free text keyword overlap
        for kw in ["coffee", "tea", "burger", "pizza", "dessert", "rooftop", "buffet"]:
            if kw in pref_free and (kw in cuisine or kw in tags_str or kw in name):
                score += 8
                reasons.append(f"matches '{kw}'")

        # Proximity bonus (closer places get a slight boost)
        dist = p.get("distance_meters", 1000)
        if dist < 500:
            score += 5

        score = min(score, 98)
        reason_text = f"Recommended ({', '.join(reasons)})" if reasons else f"Conveniently located {cat} {dist}m from meeting point."

        res = dict(p)
        res["match_score"] = score
        res["reason"] = reason_text
        scored.append(res)

    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return scored
