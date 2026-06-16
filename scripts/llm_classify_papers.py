import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_YEAR = "2026"
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_BASE_URL = "https://api.openai.com/v1"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from classify_papers import (  # noqa: E402
    TAXONOMY,
    normalize_text,
    score_rule,
    taxonomy_level2_map,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Use an OpenAI-compatible LLM API to create category overrides."
    )
    parser.add_argument("--year", default=DEFAULT_YEAR)
    parser.add_argument("--input-json", type=Path)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--model", default=os.getenv("LLM_MODEL") or os.getenv("OPENAI_MODEL") or DEFAULT_MODEL)
    parser.add_argument("--base-url", default=os.getenv("LLM_BASE_URL") or os.getenv("OPENAI_BASE_URL") or DEFAULT_BASE_URL)
    parser.add_argument("--api-key", default=os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or "")
    parser.add_argument("--batch-size", type=int, default=6)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--sleep", type=float, default=0.2)
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-no-key", action="store_true")
    return parser.parse_args()


def category_catalog():
    seen = set()
    rows = []
    for rule in TAXONOMY:
        key = rule["level2"]
        if key in seen:
            continue
        seen.add(key)
        rows.append({"category_level1": rule["level1"], "category_level2": rule["level2"]})
    return rows


def rule_candidates(row, limit=8):
    title_text = normalize_text(row.get("title", ""))
    abstract_text = normalize_text(row.get("abstract", ""))
    candidates = []
    for rule in TAXONOMY:
        score, matches, title_hits, _ = score_rule(rule, title_text, abstract_text)
        if score <= 0:
            continue
        candidates.append(
            {
                "category_level1": rule["level1"],
                "category_level2": rule["level2"],
                "score": score,
                "title_hits": title_hits,
                "signals": matches[:5],
            }
        )
    candidates.sort(
        key=lambda item: (item["score"], item["title_hits"], len(item["signals"])),
        reverse=True,
    )
    return candidates[:limit]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_existing(path):
    if not path.exists():
        return {}
    data = load_json(path)
    entries = data.get("overrides", data) if isinstance(data, dict) else data
    if isinstance(entries, dict):
        rows = []
        for title, value in entries.items():
            row = dict(value) if isinstance(value, dict) else {"category_level2": value}
            row.setdefault("title", title)
            rows.append(row)
        entries = rows
    return {entry["title"]: entry for entry in entries if entry.get("title")}


def save_overrides(path, overrides, model, base_url):
    rows = sorted(overrides.values(), key=lambda item: item["title"].lower())
    payload = {
        "source": "llm",
        "model": model,
        "base_url": base_url,
        "overrides": rows,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(path)


def chunked(rows, size):
    for start in range(0, len(rows), size):
        yield rows[start : start + size]


def build_messages(batch, catalog):
    allowed = "\n".join(
        f"- {item['category_level2']} (level1: {item['category_level1']})"
        for item in catalog
    )
    papers = []
    for index, row in enumerate(batch):
        papers.append(
            {
                "id": index,
                "title": row.get("title", ""),
                "abstract": row.get("abstract", "")[:2600],
                "rule_candidates": rule_candidates(row),
            }
        )

    system = (
        "You classify CVPR papers by their main technical contribution. "
        "Do not classify by isolated keywords. Choose exactly one category_level2 "
        "from the allowed list. If a paper is about anomaly or defect detection, "
        "prefer Classification, Retrieval & Fine-grained Recognition over generic detection. "
        "If a paper is primarily about a domain such as medical or remote sensing, "
        "prefer the domain category. Return strict JSON only."
    )
    user = (
        "Allowed categories:\n"
        f"{allowed}\n\n"
        "Papers:\n"
        f"{json.dumps(papers, ensure_ascii=False)}\n\n"
        "Return this JSON shape:\n"
        '{"decisions":[{"id":0,"category_level2":"...","reason":"short reason"}]}'
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def post_chat_completion(base_url, api_key, model, messages, timeout=120, use_response_format=True):
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0,
    }
    if use_response_format:
        payload["response_format"] = {"type": "json_object"}

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def parse_json_object(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(text[start : end + 1])


def llm_decide_batch(base_url, api_key, model, messages):
    try:
        response = post_chat_completion(base_url, api_key, model, messages)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        if "response_format" not in body:
            raise RuntimeError(body) from exc
        response = post_chat_completion(
            base_url,
            api_key,
            model,
            messages,
            use_response_format=False,
        )
    content = response["choices"][0]["message"]["content"]
    data = parse_json_object(content)
    return data.get("decisions", [])


def main():
    args = parse_args()
    data_dir = BASE_DIR / "data" / args.year
    input_json = args.input_json or (data_dir / "papers.hierarchy.json")
    if not input_json.exists():
        input_json = data_dir / "papers.json"
    out_json = args.out_json or (data_dir / "category_overrides.json")

    if not args.dry_run and not args.api_key and not args.allow_no_key:
        raise SystemExit(
            "Missing API key. Set LLM_API_KEY/OPENAI_API_KEY, or pass --allow-no-key for a local compatible server."
        )

    rows = load_json(input_json)
    if args.limit:
        rows = rows[: args.limit]

    existing = load_existing(out_json) if not args.no_resume else {}
    todo = [row for row in rows if row.get("title") and row.get("title") not in existing]
    catalog = category_catalog()
    level2_to_level1 = taxonomy_level2_map()

    print(f"loaded {len(rows)} papers")
    print(f"existing overrides: {len(existing)}")
    print(f"to classify: {len(todo)}")

    if args.dry_run:
        preview = todo[: args.batch_size]
        print(json.dumps(build_messages(preview, catalog), ensure_ascii=False, indent=2))
        return

    completed = 0
    for batch in chunked(todo, max(1, args.batch_size)):
        messages = build_messages(batch, catalog)
        decisions = llm_decide_batch(args.base_url, args.api_key, args.model, messages)
        by_id = {int(item["id"]): item for item in decisions if "id" in item}

        for index, paper in enumerate(batch):
            decision = by_id.get(index)
            if not decision:
                continue
            level2 = str(decision.get("category_level2", "")).strip()
            if level2 not in level2_to_level1:
                print(f"invalid category for {paper.get('title', '')}: {level2}")
                continue
            title = paper["title"]
            existing[title] = {
                "title": title,
                "category_level1": level2_to_level1[level2],
                "category_level2": level2,
                "source": "llm",
                "model": args.model,
                "reason": str(decision.get("reason", "")).strip(),
            }
            completed += 1

        save_overrides(out_json, existing, args.model, args.base_url)
        print(f"saved {len(existing)} overrides ({completed} new this run)")
        if args.sleep:
            time.sleep(args.sleep)

    print(f"done: {out_json}")


if __name__ == "__main__":
    main()
