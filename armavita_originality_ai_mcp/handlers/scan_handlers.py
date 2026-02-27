"""
Scan handler implementations for Originality.ai MCP Server.

Each handler calls the API client, processes the response, and returns
formatted TextContent that's useful without being overwhelming.
"""

import re
from typing import Any

from loguru import logger
from mcp.types import TextContent

from armavita_originality_ai_mcp.client import OriginalityClient


def _strip_markdown(text: str) -> str:
    """Strip markdown formatting to send clean plaintext to the API.

    Originality.ai docs: 'For the most accurate scoring provide plain text.'
    """
    # Remove bold/italic markers
    text = re.sub(r'\*{1,3}(.+?)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,3}(.+?)_{1,3}', r'\1', text)
    # Remove headings (## Heading -> Heading)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove markdown links [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Remove inline code backticks
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # Remove blockquote markers
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
    # Remove list markers (- item, * item, 1. item)
    text = re.sub(r'^[\-\*]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
    # Remove image syntax ![alt](url)
    text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', text)
    # Collapse multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


# ── AI Detection ──────────────────────────────────────────────────

async def handle_scan_ai(
    arguments: dict[str, Any],
    client: OriginalityClient,
) -> list[TextContent]:
    """AI detection scan only."""
    content = _strip_markdown(arguments.get("content", ""))
    if not content or len(content.split()) < 20:
        return [TextContent(type="text", text="Content too short — need at least ~50 words for reliable AI detection.")]

    result = await client.scan(
        content=content,
        title=arguments.get("title", "AI Detection Scan"),
        check_ai=True,
        ai_model_version=arguments.get("ai_model", "lite-102"),
    )
    return [TextContent(type="text", text=_format_ai_result(result))]


# ── Full Audit ────────────────────────────────────────────────────

async def handle_scan_full(
    arguments: dict[str, Any],
    client: OriginalityClient,
) -> list[TextContent]:
    """Comprehensive scan: AI + plagiarism + readability + grammar + facts."""
    content = _strip_markdown(arguments.get("content", ""))
    if not content:
        return [TextContent(type="text", text="No content provided.")]

    result = await client.scan(
        content=content,
        title=arguments.get("title", "Full Content Audit"),
        check_ai=True,
        check_plagiarism=True,
        check_readability=True,
        check_grammar=True,
        check_facts=arguments.get("check_facts", True),
        ai_model_version=arguments.get("ai_model", "lite-102"),
        excluded_urls=arguments.get("excluded_urls"),
    )
    return [TextContent(type="text", text=_format_full_result(result))]


# ── Plagiarism Only ───────────────────────────────────────────────

async def handle_scan_plagiarism(
    arguments: dict[str, Any],
    client: OriginalityClient,
) -> list[TextContent]:
    """Plagiarism-only scan."""
    content = _strip_markdown(arguments.get("content", ""))
    if not content:
        return [TextContent(type="text", text="No content provided.")]

    result = await client.scan(
        content=content,
        title=arguments.get("title", "Plagiarism Scan"),
        check_plagiarism=True,
        excluded_urls=arguments.get("excluded_urls"),
    )
    return [TextContent(type="text", text=_format_plagiarism_result(result))]


# ── Readability + Grammar ────────────────────────────────────────

async def handle_scan_readability(
    arguments: dict[str, Any],
    client: OriginalityClient,
) -> list[TextContent]:
    """Readability and grammar scan only."""
    content = _strip_markdown(arguments.get("content", ""))
    if not content:
        return [TextContent(type="text", text="No content provided.")]

    result = await client.scan(
        content=content,
        title=arguments.get("title", "Readability Scan"),
        check_readability=True,
        check_grammar=True,
    )
    return [TextContent(type="text", text=_format_readability_grammar(result))]


# ── SEO Optimizer ─────────────────────────────────────────────────

async def handle_scan_seo(
    arguments: dict[str, Any],
    client: OriginalityClient,
) -> list[TextContent]:
    """SEO content optimization scan."""
    content = _strip_markdown(arguments.get("content", ""))
    keyword = arguments.get("keyword", "")
    if not content:
        return [TextContent(type="text", text="No content provided.")]
    if not keyword:
        return [TextContent(type="text", text="No keyword provided. The 'keyword' parameter is required for SEO analysis.")]

    result = await client.scan(
        content=content,
        title=arguments.get("title", "SEO Scan"),
        check_ai=arguments.get("check_ai", True),
        check_readability=arguments.get("check_readability", True),
        check_content_optimizer=True,
        optimizer_query=keyword,
        optimizer_device=arguments.get("device", "desktop"),
        optimizer_publishing_domain=arguments.get("publishing_domain", ""),
        ai_model_version="lite-102",
    )
    return [TextContent(type="text", text=_format_seo_result(result, keyword))]


# ── URL Scan ──────────────────────────────────────────────────────

async def handle_scan_url(
    arguments: dict[str, Any],
    client: OriginalityClient,
) -> list[TextContent]:
    """Scan content from a published URL."""
    url = arguments.get("url", "")
    if not url:
        return [TextContent(type="text", text="No URL provided.")]

    result = await client.scan_url(
        url=url,
        title=arguments.get("title", "URL Scan"),
        check_ai=arguments.get("check_ai", True),
        check_plagiarism=arguments.get("check_plagiarism", True),
        check_readability=arguments.get("check_readability", True),
        check_grammar=arguments.get("check_grammar", True),
        check_facts=arguments.get("check_facts", False),
        ai_model_version=arguments.get("ai_model", "lite-102"),
        excluded_urls=arguments.get("excluded_urls"),
    )
    return [TextContent(type="text", text=_format_full_result(result, source_url=url))]


# ── Retrieval ─────────────────────────────────────────────────────

async def handle_get_scan_results(
    arguments: dict[str, Any],
    client: OriginalityClient,
) -> list[TextContent]:
    """Retrieve stored scan results."""
    scan_id = arguments.get("scan_id", "")
    if not scan_id:
        return [TextContent(type="text", text="No scan_id provided.")]

    result = await client.get_scan_results(scan_id)
    return [TextContent(type="text", text=_format_full_result(result))]


async def handle_credit_balance(
    arguments: dict[str, Any],
    client: OriginalityClient,
) -> list[TextContent]:
    """Check credit balance."""
    result = await client.get_credit_balance()
    balance = result.get("credits", result.get("balance", "unknown"))
    return [TextContent(type="text", text=f"**Originality.ai Credit Balance:** {balance}")]


# ══════════════════════════════════════════════════════════════════
# Response formatters
# ══════════════════════════════════════════════════════════════════

def _safe_get(data: dict, *keys: str, default: Any = None) -> Any:
    """Safely traverse nested dict keys."""
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key, default)
        else:
            return default
    return current


def _to_probability(value: Any) -> float | None:
    """Normalize a probability-like value to the 0..1 range.

    Accepts either 0..1 floats or 0..100 percentages.
    Returns None for booleans/non-numeric values.
    """
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, str):
        try:
            value = float(value.strip())
        except Exception:
            return None
    if not isinstance(value, (int, float)):
        return None

    v = float(value)
    if v < 0:
        return 0.0
    if v <= 1:
        return v
    # API variants may return whole percentages (e.g. 70 for 70%)
    if v <= 100:
        return v / 100.0
    return 1.0


def _extract_ai_probs(results: dict) -> tuple[float, float]:
    """Extract AI/Original probabilities robustly across API schema variants.

    Known issue observed in the wild: `classification` can be one-hot/bool-like
    in some responses, while confidence lives in a different score object.
    """
    ai_obj = results.get("ai", {}) if isinstance(results, dict) else {}

    candidates: list[dict[str, Any]] = []
    # confidence holds the real probability (e.g. 0.77); classification is binary (0 or 1).
    # Check confidence FIRST so it takes priority.
    if isinstance(ai_obj.get("confidence"), dict):
        candidates.append(ai_obj["confidence"])
    if isinstance(ai_obj.get("score"), dict):
        candidates.append(ai_obj["score"])
    if isinstance(ai_obj.get("scores"), dict):
        candidates.append(ai_obj["scores"])
    if isinstance(ai_obj.get("probability"), dict):
        candidates.append(ai_obj["probability"])
    if isinstance(results.get("score"), dict):
        candidates.append(results["score"])
    # classification is binary (0/1) — only use as last resort
    if isinstance(ai_obj.get("classification"), dict):
        candidates.append(ai_obj["classification"])
    if isinstance(results.get("classification"), dict):
        candidates.append(results["classification"])

    ai_keys = ("AI", "ai", "fake", "generated", "ai_score", "confidence_ai")
    original_keys = (
        "Original",
        "original",
        "human",
        "human_written",
        "real",
        "original_score",
        "confidence_original",
    )

    for bucket in candidates:
        ai_raw = next((bucket.get(k) for k in ai_keys if k in bucket), None)
        orig_raw = next((bucket.get(k) for k in original_keys if k in bucket), None)

        ai_prob = _to_probability(ai_raw)
        orig_prob = _to_probability(orig_raw)

        # Prefer candidates with at least one non-boolean numeric probability.
        if ai_prob is None and orig_prob is None:
            continue
        if ai_prob is None and orig_prob is not None:
            ai_prob = max(0.0, min(1.0, 1.0 - orig_prob))
        elif orig_prob is None and ai_prob is not None:
            orig_prob = max(0.0, min(1.0, 1.0 - ai_prob))

        # If both values exist but are not complementary due to schema drift,
        # renormalize to keep output sane for the UI/LLM.
        total = (ai_prob or 0.0) + (orig_prob or 0.0)
        if total > 0 and (total < 0.98 or total > 1.02):
            ai_prob = (ai_prob or 0.0) / total
            orig_prob = (orig_prob or 0.0) / total

        return ai_prob or 0.0, orig_prob or 0.0

    return 0.0, 0.0


def _format_ai_result(data: dict) -> str:
    """Format AI detection results."""
    results = data.get("results", data)
    ai = results.get("ai", {})
    credits_used = _safe_get(results, "credits", "used", default="?")
    ai_pct, original_pct = _extract_ai_probs(results)
    model = ai.get("aiModel", "unknown")

    lines = [
        "## AI Detection Results",
        "",
        f"| Metric | Score |",
        f"|--------|-------|",
        f"| AI Content | **{ai_pct:.0%}** |",
        f"| Original Content | **{original_pct:.0%}** |",
        f"| Model Used | {model} |",
        f"| Credits Used | {credits_used} |",
        "",
    ]

    # Verdict
    if ai_pct >= 0.75:
        lines.append("**Verdict:** High AI probability — significant revision recommended before publishing.")
    elif ai_pct >= 0.5:
        lines.append("**Verdict:** Mixed signals — some sections flagged as AI. Review flagged sentences below.")
    elif ai_pct >= 0.25:
        lines.append("**Verdict:** Mostly original with minor AI signals. Light revision may help.")
    else:
        lines.append("**Verdict:** Content reads as original.")

    # Sentence-level breakdown (top flagged sentences)
    blocks = ai.get("blocks", [])
    flagged = [b for b in blocks if b.get("result", {}).get("fake", 0) > 0.5]

    if flagged:
        lines.append("")
        lines.append(f"### Flagged Sentences ({len(flagged)} of {len(blocks)} total)")
        lines.append("")
        for block in flagged:
            text = block.get("text", "")[:120]
            fake_score = block.get("result", {}).get("fake", 0)
            lines.append(f"- **{fake_score:.0%} AI** — \"{text}{'...' if len(block.get('text', '')) > 120 else ''}\"")


    # Scan ID for retrieval
    scan_id = results.get("id", "")
    if scan_id:
        lines.extend(["", f"*Scan ID: {scan_id}*"])

    return "\n".join(lines)


def _format_readability_grammar(data: dict) -> str:
    """Format readability and grammar results."""
    results = data.get("results", data)
    lines = ["## Readability & Grammar Results", ""]

    # Readability
    readability = results.get("readability", {})
    stats = readability.get("text_stats", {})
    if stats:
        flesch = stats.get("fleschReadingEase", "N/A")
        grade = stats.get("fleschGradeLevel", "N/A")
        gunning = stats.get("gunningFoxIndex", "N/A")
        sentences = stats.get("sentenceCount", "N/A")
        words = stats.get("uniqueWordCount", "N/A")

        # Target check
        if isinstance(flesch, (int, float)):
            if 60 <= flesch <= 70:
                flesch_status = "(on target)"
            elif flesch > 70:
                flesch_status = "(simpler than target)"
            else:
                flesch_status = "(harder than target — aim for 60-70)"
        else:
            flesch_status = ""

        if isinstance(grade, (int, float)):
            if 8 <= grade <= 9:
                grade_status = "(on target)"
            elif grade < 8:
                grade_status = "(below target)"
            else:
                grade_status = "(above target — aim for 8th-9th grade)"
        else:
            grade_status = ""

        lines.extend([
            "### Readability Scores",
            "",
            "| Metric | Score | Status |",
            "|--------|-------|--------|",
            f"| Flesch Reading Ease | {flesch} | {flesch_status} |",
            f"| Flesch Grade Level | {grade} | {grade_status} |",
            f"| Gunning Fog Index | {gunning} | |",
            f"| Sentences | {sentences} | |",
            f"| Unique Words | {words} | |",
            "",
        ])

    # Hard-to-read sentences
    hard_sentences = readability.get("sentences", [])
    very_hard = [s for s in hard_sentences if s.get("isVeryHard")]
    hard = [s for s in hard_sentences if s.get("isHard") and not s.get("isVeryHard")]

    if very_hard or hard:
        lines.append("### Difficult Sentences")
        lines.append("")
        if very_hard:
            lines.append(f"**Very Hard ({len(very_hard)}):**")
            for s in very_hard[:5]:
                phrase = s.get("phrase", "")[:150]
                lines.append(f"- \"{phrase}{'...' if len(s.get('phrase', '')) > 150 else ''}\"")
            if len(very_hard) > 5:
                lines.append(f"- ... and {len(very_hard) - 5} more")
            lines.append("")
        if hard:
            lines.append(f"**Hard ({len(hard)}):**")
            for s in hard[:5]:
                phrase = s.get("phrase", "")[:150]
                lines.append(f"- \"{phrase}{'...' if len(s.get('phrase', '')) > 150 else ''}\"")
            if len(hard) > 5:
                lines.append(f"- ... and {len(hard) - 5} more")
            lines.append("")

    # Grammar
    grammar = results.get("grammarSpelling", {})
    matches = grammar.get("matches", [])
    score = grammar.get("score", "N/A")
    grade = grammar.get("grade", "N/A")

    if matches or score != "N/A":
        lines.extend([
            "### Grammar & Spelling",
            "",
            f"**Score:** {score} | **Grade:** {grade} | **Issues Found:** {len(matches)}",
            "",
        ])
        if matches:
            for m in matches[:10]:
                msg = m.get("message", "")
                sentence = m.get("sentence", "")[:100]
                replacements = m.get("replacements", [])
                fix = replacements[0].get("value", "") if replacements else ""
                lines.append(f"- {msg}")
                if sentence:
                    lines.append(f"  - In: \"{sentence}{'...' if len(m.get('sentence', '')) > 100 else ''}\"")
                if fix:
                    lines.append(f"  - Suggested: **{fix}**")
            if len(matches) > 10:
                lines.append(f"- ... and {len(matches) - 10} more issues")

    return "\n".join(lines)


def _format_seo_result(data: dict, keyword: str) -> str:
    """Format SEO optimizer results (plus optional AI + readability)."""
    results = data.get("results", data)
    lines = [f"## SEO Analysis: \"{keyword}\"", ""]

    # Content optimizer
    optimizer = results.get("contentOptimizer", {})
    seeds = optimizer.get("keyword_seeds", [])

    if seeds:
        lines.extend([
            "### Keyword Density Targets",
            "",
            "| Keyword | Current | Min | Max | Status |",
            "|---------|---------|-----|-----|--------|",
        ])
        for seed in seeds:
            kw = seed.get("keyword", "")
            current = seed.get("current", 0)
            mn = seed.get("min", 0)
            mx = seed.get("max", 0)
            if current < mn:
                status = "Under-optimized"
            elif current > mx:
                status = "Over-optimized"
            else:
                status = "Good"
            lines.append(f"| {kw} | {current} | {mn} | {mx} | {status} |")
        lines.append("")

    # AI detection if included
    ai = results.get("ai", {})
    if ai and (
        ai.get("classification")
        or ai.get("score")
        or ai.get("scores")
        or ai.get("probability")
    ):
        ai_pct, original_pct = _extract_ai_probs(results)
        lines.extend([
            "### AI Detection",
            "",
            f"- AI: **{ai_pct:.0%}** | Original: **{original_pct:.0%}**",
            "",
        ])

    # Readability if included
    readability = results.get("readability", {})
    stats = readability.get("text_stats", {})
    if stats:
        flesch = stats.get("fleschReadingEase", "N/A")
        grade = stats.get("fleschGradeLevel", "N/A")
        lines.extend([
            "### Readability",
            "",
            f"- Flesch Reading Ease: **{flesch}** | Grade Level: **{grade}**",
            "",
        ])

    # Credits
    credits_used = _safe_get(results, "credits", "used", default="?")
    lines.append(f"*Credits used: {credits_used}*")

    # Scan ID
    scan_id = results.get("id", "")
    if scan_id:
        lines.append(f"*Scan ID: {scan_id}*")

    return "\n".join(lines)


def _format_full_result(data: dict, source_url: str = "") -> str:
    """Format a comprehensive scan result with all available sections."""
    results = data.get("results", data)
    credits_used = _safe_get(results, "credits", "used", default="?")

    header = "## Content Audit Results"
    if source_url:
        header += f"\n**Source:** {source_url}"
    lines = [header, ""]

    # ── Summary table ──
    summary_rows = []
    ai = results.get("ai", {})
    if ai and (
        ai.get("classification")
        or ai.get("score")
        or ai.get("scores")
        or ai.get("probability")
    ):
        ai_pct, original_pct = _extract_ai_probs(results)
        summary_rows.append(f"| AI Detection | **{original_pct:.0%} Original** / {ai_pct:.0%} AI |")

    plagiarism = results.get("plagiarism", {})
    plag_score = plagiarism.get("score")
    if plag_score is not None:
        summary_rows.append(f"| Plagiarism | **{plag_score}%** matched |")

    readability = results.get("readability", {})
    stats = readability.get("text_stats", {})
    if stats:
        flesch = stats.get("fleschReadingEase", "N/A")
        grade = stats.get("fleschGradeLevel", "N/A")
        summary_rows.append(f"| Readability | Flesch **{flesch}** / Grade **{grade}** |")

    grammar = results.get("grammarSpelling", {})
    if grammar:
        g_score = grammar.get("score", "N/A")
        g_grade = grammar.get("grade", "N/A")
        g_issues = len(grammar.get("matches", []))
        summary_rows.append(f"| Grammar | Score **{g_score}** ({g_grade}) — {g_issues} issues |")

    if summary_rows:
        lines.extend([
            "| Check | Result |",
            "|-------|--------|",
        ])
        lines.extend(summary_rows)
        lines.extend(["", f"*Credits used: {credits_used}*", ""])

    # ── AI detail ──
    if ai and ai.get("blocks"):
        lines.append(_format_ai_result({"results": results}).split("## AI Detection Results\n")[-1])
        lines.append("")

    # ── Plagiarism detail ──
    plag_results = plagiarism.get("results", [])
    if plag_results:
        lines.append("### Plagiarism Sources")
        lines.append("")
        source_count = 0
        for phrase_group in plag_results:
            for match in phrase_group.get("results", []):
                link = match.get("link", "")
                title = match.get("title", link)
                scores = match.get("scores", [])
                top_score = max((s.get("score", 0) for s in scores), default=0)
                if top_score > 0:
                    lines.append(f"- **{top_score:.0%}** match — [{title}]({link})")
                    source_count += 1
                    if source_count >= 10:
                        break
            if source_count >= 10:
                break
        lines.append("")

    # ── Facts ──
    facts = results.get("facts", [])
    if facts:
        lines.append("### Fact Check")
        lines.append("")
        for fact in facts[:10]:
            claim = fact.get("fact", "")
            truthfulness = fact.get("truthfulness", "?")
            explanation = fact.get("explanation", "")[:200]
            lines.append(f"- **{truthfulness}** — {claim}")
            if explanation:
                lines.append(f"  - {explanation}")
        if len(facts) > 10:
            lines.append(f"- ... and {len(facts) - 10} more claims checked")
        lines.append("")

    # ── Readability + grammar detail (only if not already covered in summary) ──
    # Include hard sentences and grammar fixes
    hard_sentences = readability.get("sentences", [])
    very_hard = [s for s in hard_sentences if s.get("isVeryHard")]
    if very_hard:
        lines.append(f"### Very Hard Sentences ({len(very_hard)})")
        lines.append("")
        for s in very_hard[:5]:
            phrase = s.get("phrase", "")[:150]
            lines.append(f"- \"{phrase}{'...' if len(s.get('phrase', '')) > 150 else ''}\"")
        if len(very_hard) > 5:
            lines.append(f"- ... and {len(very_hard) - 5} more")
        lines.append("")

    grammar_matches = grammar.get("matches", [])
    if grammar_matches:
        lines.append(f"### Grammar Issues ({len(grammar_matches)})")
        lines.append("")
        for m in grammar_matches[:8]:
            msg = m.get("message", "")
            replacements = m.get("replacements", [])
            fix = replacements[0].get("value", "") if replacements else ""
            sentence = m.get("sentence", "")[:100]
            lines.append(f"- {msg}")
            if fix:
                lines.append(f"  - Fix: **{fix}**")
        if len(grammar_matches) > 8:
            lines.append(f"- ... and {len(grammar_matches) - 8} more")
        lines.append("")

    # Scan ID
    scan_id = results.get("id", "")
    if scan_id:
        lines.append(f"*Scan ID: {scan_id}*")

    return "\n".join(lines)


def _format_plagiarism_result(data: dict) -> str:
    """Format plagiarism-only scan results."""
    results = data.get("results", data)
    credits_used = _safe_get(results, "credits", "used", default="?")

    plagiarism = results.get("plagiarism", {})
    plag_score = plagiarism.get("score")

    lines = ["## Plagiarism Check Results", ""]

    if plag_score is not None:
        if plag_score == 0:
            verdict = "No plagiarism detected."
        elif plag_score < 10:
            verdict = "Minor matches — likely common phrasing."
        elif plag_score < 25:
            verdict = "Moderate overlap — review matched sources."
        else:
            verdict = "Significant plagiarism detected — revision needed."

        lines.extend([
            f"**Plagiarism Score:** {plag_score}%",
            f"**Verdict:** {verdict}",
            f"*Credits used: {credits_used}*",
            "",
        ])
    else:
        lines.append("No plagiarism data returned.")
        lines.append("")

    # Source matches
    plag_results = plagiarism.get("results", [])
    if plag_results:
        lines.append("### Matched Sources")
        lines.append("")
        source_count = 0
        for phrase_group in plag_results:
            for match in phrase_group.get("results", []):
                link = match.get("link", "")
                title = match.get("title", link)
                scores = match.get("scores", [])
                top_score = max((s.get("score", 0) for s in scores), default=0)
                if top_score > 0:
                    lines.append(f"- **{top_score:.0%}** match — [{title}]({link})")
                    source_count += 1
                    if source_count >= 10:
                        break
            if source_count >= 10:
                break
        lines.append("")

    # Scan ID
    scan_id = results.get("id", "")
    if scan_id:
        lines.append(f"*Scan ID: {scan_id}*")

    return "\n".join(lines)
