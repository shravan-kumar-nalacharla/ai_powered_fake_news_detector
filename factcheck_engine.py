# factcheck_engine.py
"""
Tejas Engine v4.1 (Logic-Enhanced & Safety-Patched)
NO NEW LIBS. Uses existing transformers/ddgs/standard-lib.

IMPROVEMENTS:
1. "Sagan Filter": Raises evidence threshold for extreme claims (fixes "exploding trees").
2. Safety Override: Detects scam patterns and forces high-risk warnings (fixes "bot call").
3. Keyword Optimization: Cleans natural language anecdotes into effective search queries.
4. Weighted Authority: 1 Gov source > 10 Blogs.
5. Radical Transparency: Returns the exact snippet used for the verdict.
"""

print("\n--- LOADING TEJAS ENGINE V4.1 (SAFETY PATCHED) ---\n")

import re
import time
import hashlib
from typing import List, Dict, Any, Tuple
from urllib.parse import urlparse
from threading import Lock

# Existing dependencies
from ddgs import DDGS
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util

# =====================
# CONFIG & CONSTANTS
# =====================
CLASSIFIER_MODEL = "shravan1nala/tejas-fake-news-model-v3"
EMBEDDER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
NLI_MODEL = "roberta-large-mnli"

MAX_EVIDENCE = 15
TOP_K = 5

# "Sagan Words" - Triggers higher burden of proof (Threshold 1.5)
EXTREME_MARKERS = {
    "overnight", "immediately", "miracle", "cure", "100%", "everyone", 
    "nobody", "destroyed", "proof", "proven", "secret", "banned",
    "explode", "exploding", "massive", "tremendous", "by a lot", "vastly"
}

# Safety Triggers - Forces a "Scam" check
SAFETY_TRIGGERS = {
    "received a call", "asked for", "verification code", "otp", "bank account",
    "credit card", "won a", "urgent", "immediate action", "police", "arrest",
    "customer service", "bot", "refund"
}

_CACHE: Dict[str, Any] = {}
_LOCK = Lock()

print("Loading models...")
# CPU execution (device=-1)
classifier = pipeline("text-classification", model=CLASSIFIER_MODEL)
embedder = SentenceTransformer(EMBEDDER_MODEL)
nli = pipeline("text-classification", model=NLI_MODEL)
print("Models loaded.")


# =====================
# CORE UTILS
# =====================
def get_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except:
        return ""

def calculate_authority(url: str) -> float:
    """
    Returns authority score [0.1 - 1.0].
    """
    d = get_domain(url)
    
    # Tier 1: Gov/Edu/Mil (The "Gold Standard")
    if any(x in d for x in [".gov", ".mil", ".edu", ".nic.in", "who.int", "un.org"]):
        return 1.0
        
    # Tier 2: Major Wires & Legacy (High Trust)
    trusted = [
        "reuters", "apnews", "bbc", "bloomberg", "afp", "nature.com", "sciencemag",
        "thehindu", "indianexpress", "timesofindia", "ndtv", "ddnews", "ptinews",
        "nytimes", "wsj.com", "economist", "mayoclinic", "webmd", "telanganatoday",
        "altnews.in", "boomlive.in", "snopes.com", "politifact.com"
    ]
    if any(t in d for t in trusted):
        return 0.85
        
    # Tier 3: Wikipedia/Crowd (Medium Trust)
    if "wikipedia.org" in d:
        return 0.6
        
    # Tier 4: General Web (Low Trust)
    return 0.3

def extract_years(text: str) -> set:
    return set(re.findall(r"\b(20\d{2})\b", text))

def is_claim_extreme(claim: str) -> bool:
    """Checks if claim contains sensationalist language."""
    words = set(re.findall(r"\w+", claim.lower()))
    return bool(words.intersection(EXTREME_MARKERS))

def extract_search_keywords(text: str) -> str:
    """
    Turns natural language anecdotes into search-friendly queries.
    Input: "I received a call from a bot asking for my code"
    Output: "bot asking for code scam fraud alert"
    """
    # 1. Check for Scam Intent
    is_safety_check = any(t in text.lower() for t in SAFETY_TRIGGERS)
    
    # Remove stopwords to help DuckDuckGo focus on entities
    stopwords = {"i", "me", "my", "received", "a", "the", "from", "that", "this", "is", "was", "an", "has", "have"}
    words = re.findall(r"\w+", text.lower())
    keywords = [w for w in words if w not in stopwords]
    
    query = " ".join(keywords)
    
    # 2. Safety Injection: If it sounds like a scam, FORCE the word 'scam' into search
    if is_safety_check:
        query += " scam fraud alert"
        
    return query


# =====================
# SEARCH & RANKING
# =====================
def search_web(user_claim: str) -> List[Dict[str, Any]]:
    """
    Performs search using optimized keywords and dedups by domain.
    """
    # USE THE CLEANED QUERY, NOT THE RAW CLAIM
    optimized_query = extract_search_keywords(user_claim)
    # Optional: Print debug info if needed
    # print(f"DEBUG: Searching for '{optimized_query}'")
    
    raw_results = []
    seen_domains = set()
    
    try:
        with DDGS() as ddgs:
            # 'in-en' for India focus, or None for global
            for r in ddgs.text(optimized_query, max_results=MAX_EVIDENCE, region='in-en'):
                url = r.get("href", "")
                if not url: continue
                
                dom = get_domain(url)
                if dom in seen_domains: continue
                seen_domains.add(dom)
                
                raw_results.append({
                    "url": url,
                    "domain": dom,
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                    "authority": calculate_authority(url)
                })
    except Exception as e:
        print(f"[SEARCH ERROR] {e}")
        
    return raw_results

def semantic_rank(claim: str, evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ranks evidence by semantic similarity + authority.
    """
    if not evidence: return []
    
    snippets = [f"{e['title']} : {e['snippet']}" for e in evidence]
    
    # Vectorize
    claim_vec = embedder.encode(claim, convert_to_tensor=True)
    doc_vecs = embedder.encode(snippets, convert_to_tensor=True)
    
    # Cosine Similarity
    scores = util.cos_sim(claim_vec, doc_vecs)[0]
    
    ranked = []
    for i, e in enumerate(evidence):
        score = float(scores[i])
        e["similarity"] = score
        # Hybrid Score: Similarity * Authority
        # High authority boosts the rank of a snippet
        e["relevance_score"] = score * (1 + e["authority"]) 
        ranked.append(e)
        
    # Sort by relevance
    return sorted(ranked, key=lambda x: x["relevance_score"], reverse=True)


# =====================
# LOGIC & NLI
# =====================
def check_entailment(claim: str, evidence_text: str) -> Tuple[str, float]:
    """
    Returns (Label, Confidence).
    Labels: ENTAIL, CONTRA, NEUTRAL
    """
    if not evidence_text: return "NEUTRAL", 0.0

    # Cache check
    h = hashlib.md5((claim + evidence_text).encode()).hexdigest()
    with _LOCK:
        if h in _CACHE: return _CACHE[h]

    input_text = f"{evidence_text} </s></s> {claim}"
    try:
        res = nli(input_text, truncation=True)
        # Handle list or dict return
        top = res[0] if isinstance(res, list) else res
        
        lbl = top['label'].lower()
        score = top['score']
        
        # Map Roberta labels to standard logic
        if "contradiction" in lbl:
            verdict = "CONTRA"
        elif "entailment" in lbl:
            verdict = "ENTAIL"
        else:
            verdict = "NEUTRAL"
            
        with _LOCK:
            _CACHE[h] = (verdict, score)
            
        return verdict, score
    except:
        return "NEUTRAL", 0.0

def analyze_temporal_validity(claim: str, snippet: str) -> bool:
    """
    Returns False if snippet is outdated relative to claim.
    """
    c_years = extract_years(claim)
    s_years = extract_years(snippet)
    
    # If claim has specific year (e.g. 2026) and snippet has ONLY older years (e.g. 2024), reject.
    if c_years and s_years:
        max_claim = max(int(y) for y in c_years)
        max_snip = max(int(y) for y in s_years)
        if max_snip < max_claim - 1: # Allow 1 year buffer
            return False
    return True


# =====================
# VERDICT ENGINE
# =====================
def derive_verdict(claim: str, ranked_evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
    support_score = 0.0
    refute_score = 0.0
    
    supporting_snippets = []
    refuting_snippets = []
    
    # 1. SAFETY & SCAM CHECK (Priority 1)
    is_safety_query = any(t in claim.lower() for t in SAFETY_TRIGGERS)
    scam_evidence = [
        d for d in ranked_evidence 
        if "scam" in d['title'].lower() or "fraud" in d['title'].lower()
    ]
    
    if is_safety_query and scam_evidence:
        return {
            "status": "HIGH RISK / SCAM",
            "reason": "Multiple sources identify this pattern as a known fraud tactic.",
            "evidence": scam_evidence[:3]
        }

    # 2. Determine Burden of Proof
    is_extreme = is_claim_extreme(claim)
    threshold = 1.5 if is_extreme else 0.8
    
    processed_count = 0
    
    for doc in ranked_evidence[:TOP_K]:
        # Date Logic
        if not analyze_temporal_validity(claim, doc['snippet']):
            continue
            
        # NLI Logic
        label, conf = check_entailment(claim, doc['snippet'])
        
        # Weighting: Authority * NLI Confidence
        impact = doc['authority'] * conf
        
        if label == "ENTAIL":
            support_score += impact
            supporting_snippets.append(doc)
        elif label == "CONTRA":
            refute_score += impact
            refuting_snippets.append(doc)
            
        processed_count += 1

    # 3. Final Decision Logic
    
    # GOV/OFFICIAL OVERRIDE
    gov_refutes = any(d['authority'] == 1.0 for d in refuting_snippets)
    gov_supports = any(d['authority'] == 1.0 for d in supporting_snippets)
    
    if gov_refutes:
        return {
            "status": "FALSE", 
            "reason": "Officially debunked by government/authoritative source.",
            "evidence": refuting_snippets[:2]
        }
    
    if gov_supports:
        return {
            "status": "TRUE", 
            "reason": "Confirmed by official government/authoritative source.",
            "evidence": supporting_snippets[:2]
        }

    # STANDARD SCORING
    if support_score < 0.3 and refute_score < 0.3:
        return {
            "status": "INSUFFICIENT_EVIDENCE",
            "reason": "No reliable matching evidence found in current timeframe.",
            "evidence": []
        }
        
    if is_extreme and support_score < threshold:
         # Sagan Standard: Extraordinary claims need extraordinary evidence
         return {
            "status": "UNVERIFIED / EXAGGERATED",
            "reason": "Claim contains extreme language but lacks high-authority consensus.",
            "evidence": supporting_snippets[:2]
        }

    if support_score > refute_score + 0.5:
        return {"status": "TRUE", "reason": "Consensus of sources supports this claim.", "evidence": supporting_snippets[:2]}
        
    if refute_score > support_score + 0.5:
        return {"status": "FALSE", "reason": "Multiple sources contradict this claim.", "evidence": refuting_snippets[:2]}

    return {
        "status": "DISPUTED", 
        "reason": "Sources are conflicted or context is missing.",
        "evidence": ranked_evidence[:3]
    }


# =====================
# API
# =====================
def fact_check(text: str) -> Dict[str, Any]:
    """
    Main entry point.
    """
    t0 = time.time()
    claim = text.strip()
    
    # 1. Search (Optimized)
    raw_ev = search_web(claim)
    
    # 2. Rank (Weighted)
    ranked_ev = semantic_rank(claim, raw_ev)
    
    # 3. Verdict (Logic Enhanced)
    decision = derive_verdict(claim, ranked_ev)
    
    # 4. Format Output for Frontend ("Radical Transparency")
    formatted_sources = []
    for item in decision.get("evidence", []):
        formatted_sources.append({
            "source": item['domain'],
            "authority_tier": "High" if item['authority'] >= 0.8 else "General",
            "excerpt": item['snippet'],
            "url": item['url']
        })

    return {
        "claim_analyzed": claim,
        "verdict": decision['status'],
        "summary": decision['reason'],
        "transparency_trail": formatted_sources,
        "meta": {
            "latency": round(time.time() - t0, 2),
            "sources_scanned": len(raw_ev),
            "algorithm_version": "v4.1-SafetyPatched"
        }
    }