#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TrainPPTAgent 自动评估脚本。"""
from __future__ import annotations
import argparse, asyncio, csv, json, re, statistics, time
from pathlib import Path
import httpx

ROOT = Path(__file__).resolve().parent
DATASET = ROOT / "auto_eval_dataset_100.json"
SUMMARY = ROOT / "auto_eval_summary.json"
DETAIL_JSON = ROOT / "auto_eval_results.json"
DETAIL_CSV = ROOT / "auto_eval_results.csv"
REQ = {"cover": ["data", "data.title", "data.text"], "contents": ["data", "data.items"], "transition": ["data", "data.title", "data.text"], "content": ["data", "data.title", "data.items"], "end": []}
TEXT_KEYS = {"title", "text", "content", "subtitle", "summary", "name"}

def count_units(text: str) -> int: return len(re.sub(r"\s+", "", text or ""))

def getv(data, path):
    cur = data
    for p in path.split("."):
        if not isinstance(cur, dict) or p not in cur: return None
        cur = cur[p]
    return cur

def flat_text(v):
    out = []
    def walk(x):
        if isinstance(x, dict):
            for k, y in x.items():
                if k in TEXT_KEYS and isinstance(y, str): out.append(y)
                walk(y)
        elif isinstance(x, list):
            for y in x: walk(y)
    walk(v)
    return "\n".join(out)

def field_rate(slides):
    ok = total = 0
    for s in slides:
        for p in REQ.get(s.get("type"), []):
            total += 1; v = getv(s, p)
            if isinstance(v, (str, list, dict)) and v: ok += 1
    return ok / total if total else 0.0

def word_limit(slides, lim):
    checked = bad = 0
    def ck(text, key):
        nonlocal checked, bad
        if key in lim:
            checked += 1
            if count_units(str(text)) > lim[key]: bad += 1
    for s in slides:
        d = s.get("data") if isinstance(s.get("data"), dict) else {}
        t = s.get("type")
        if t == "cover": ck(d.get("title", ""), "cover_title"); ck(d.get("text", ""), "cover_text")
        elif t == "transition": ck(d.get("title", ""), "transition_title"); ck(d.get("text", ""), "transition_text")
        elif t == "content":
            ck(d.get("title", ""), "content_title")
            for item in d.get("items", []):
                if isinstance(item, dict): ck(item.get("title", ""), "item_title"); ck(item.get("text", ""), "item_text")
    return bad, checked, bad / checked if checked else 0.0

def keyword_quality(text, kws):
    if not kws: return 1.0, []
    hits = [k for k in kws if k.lower() in text.lower()]
    return len(hits) / len(kws), hits

def simulate_edit(slides, sample):
    bads = sample.get("user_modification_rules", {}).get("forbidden_phrases", [])
    lim = sample.get("max_words_per_page", {})
    out = json.loads(json.dumps(slides, ensure_ascii=False))
    def clean(text, limit=None):
        x = str(text)
        for p in bads: x = x.replace(p, "")
        return (x[:limit] if limit and count_units(x) > limit else x).strip()
    for s in out:
        d = s.get("data")
        if not isinstance(d, dict): continue
        if s.get("type") == "cover":
            if "title" in d: d["title"] = clean(d["title"], lim.get("cover_title"))
            if "text" in d: d["text"] = clean(d["text"], lim.get("cover_text"))
        elif s.get("type") == "transition":
            if "title" in d: d["title"] = clean(d["title"], lim.get("transition_title"))
            if "text" in d: d["text"] = clean(d["text"], lim.get("transition_text"))
        elif s.get("type") == "content":
            if "title" in d: d["title"] = clean(d["title"], lim.get("content_title"))
            for item in d.get("items", []):
                if isinstance(item, dict):
                    if "title" in item: item["title"] = clean(item["title"], lim.get("item_title"))
                    if "text" in item: item["text"] = clean(item["text"], lim.get("item_text"))
    return out

def modification_rate(a, b):
    sa = json.dumps(a, ensure_ascii=False, sort_keys=True); sb = json.dumps(b, ensure_ascii=False, sort_keys=True)
    return 0.0 if sa == sb else min(1.0, abs(len(sa) - len(sb)) / max(len(sa), len(sb), 1) + 0.05)

def parse_outline(text):
    m = re.search(r"(^# .*)", text, flags=re.M | re.S)
    return text[m.start():].strip() if m else ""

def ref_outline(sample, field):
    outline = sample.get(field, "")
    return outline.strip() if isinstance(outline, str) else ""

def failed(sample, started_at, error, outline="", outline_valid=False, mode="e2e"):
    return {"id": sample["id"], "topic": sample["topic"], "mode": mode, "outline": outline, "outline_valid": outline_valid, "content_valid": False, "latency_seconds": round(time.perf_counter() - started_at, 3), "retries_used": 0, "json_valid_rate": None, "field_completeness_rate": None, "over_limit_rate": None, "over_limit_count": 0, "checked_text_count": 0, "retrieval_hit_quality": None, "hit_keywords": [], "user_final_modification_rate": None, "slide_count": 0, "slide_types": [], "parse_success": 0, "parse_failed": 0, "error": error, "slides": [], "simulated_user_final_slides": []}

async def fetch_outline(client, base_url, timeout, sample):
    payload = {"content": sample["topic"], "language": sample.get("language", "中文"), "model": "auto-eval", "stream": True}
    chunks = []
    async with client.stream("POST", f"{base_url}/tools/aippt_outline", json=payload, timeout=timeout) as r:
        r.raise_for_status()
        try:
            async for t in r.aiter_text():
                if t: chunks.append(t)
        except httpx.HTTPError:
            if not chunks: raise
    raw = "".join(chunks)
    return parse_outline(raw), raw

async def fetch_content(client, base_url, timeout, sample, outline):
    payload = {"content": outline, "language": sample.get("language", "中文"), "sessionId": sample.get("id", "auto_eval"), "generateFromUploadedFile": sample.get("generateFromUploadedFile", False), "generateFromWebSearch": sample.get("generateFromWebSearch", True)}
    slides = []; ok = bad = 0
    async with client.stream("POST", f"{base_url}/tools/aippt", json=payload, timeout=timeout) as r:
        r.raise_for_status()
        try:
            async for line in r.aiter_lines():
                if not line or line.startswith(":") or not line.startswith("data:"): continue
                data = line[5:].strip()
                if not data or data == "[DONE]": continue
                try:
                    obj = json.loads(data); ok += 1
                    if isinstance(obj, dict) and obj.get("type"): slides.append(obj)
                except json.JSONDecodeError: bad += 1
        except httpx.HTTPError:
            if not slides and ok == 0 and bad == 0: raise
    return slides, ok, bad

async def eval_one(sample, sem, args):
    async with sem:
        if args.request_interval: await asyncio.sleep(args.request_interval)
        t0 = time.perf_counter(); last_error = ""; slides = []; ok = bad = 0; retries = 0
        if args.mode == "slides-only":
            outline = ref_outline(sample, args.outline_field)
            if not outline: return failed(sample, t0, f"slides-only模式缺少参考大纲字段: {args.outline_field}", mode=args.mode)
            outline_valid = True
        else:
            async with httpx.AsyncClient() as client:
                try: outline, raw_outline = await fetch_outline(client, args.base_url, args.timeout, sample)
                except Exception as e: return failed(sample, t0, f"outline阶段失败: {e}", mode=args.mode)
            if not outline: return failed(sample, t0, "outline未生成有效Markdown大纲", raw_outline[:500], False, args.mode)
            outline_valid = True
        async with httpx.AsyncClient() as client:
            for i in range(args.max_retries + 1):
                try:
                    slides, ok, bad = await fetch_content(client, args.base_url, args.timeout, sample, outline)
                    need = set(sample.get("required_slide_types", [])); got = {s.get("type") for s in slides}
                    if need.issubset(got): retries = i; last_error = ""; break
                    last_error = f"缺少页面类型: {sorted(need - got)}"; retries = i + 1
                except Exception as e: last_error = str(e); retries = i + 1
        text = flat_text(slides); over_cnt, checked_cnt, over_rate = word_limit(slides, sample.get("max_words_per_page", {})); hit_q, hit_kws = keyword_quality(text, sample.get("expected_keywords", [])); edited = simulate_edit(slides, sample); total_json = ok + bad
        return {"id": sample["id"], "topic": sample["topic"], "mode": args.mode, "outline": outline, "outline_valid": outline_valid, "content_valid": bool(slides and not last_error), "latency_seconds": round(time.perf_counter() - t0, 3), "retries_used": retries, "json_valid_rate": round(ok / total_json, 4) if total_json else 0.0, "field_completeness_rate": round(field_rate(slides), 4), "over_limit_rate": round(over_rate, 4), "over_limit_count": over_cnt, "checked_text_count": checked_cnt, "retrieval_hit_quality": round(hit_q, 4), "hit_keywords": hit_kws, "user_final_modification_rate": round(modification_rate(slides, edited), 4), "slide_count": len(slides), "slide_types": [s.get("type") for s in slides], "parse_success": ok, "parse_failed": bad, "error": last_error, "slides": slides, "simulated_user_final_slides": edited}

def mean_or_none(values):
    values = [v for v in values if v is not None]
    return round(statistics.fmean(values), 4) if values else None

def agg(results, args):
    success = [x for x in results if x.get("content_valid")]
    return {"mode": args.mode, "outline_field": args.outline_field if args.mode == "slides-only" else None, "sample_count": len(results), "outline_valid_count": sum(1 for x in results if x.get("outline_valid")), "content_valid_count": len(success), "success_count": len(success), "failure_count": sum(1 for x in results if not x.get("content_valid")), "average_latency_seconds_all": round(statistics.fmean(x["latency_seconds"] for x in results), 4) if results else 0.0, "average_retries_all": round(statistics.fmean(x["retries_used"] for x in results), 4) if results else 0.0, "json_valid_rate_on_success": mean_or_none([x.get("json_valid_rate") for x in success]), "field_completeness_rate_on_success": mean_or_none([x.get("field_completeness_rate") for x in success]), "over_limit_rate_on_success": mean_or_none([x.get("over_limit_rate") for x in success]), "retrieval_hit_quality_on_success": mean_or_none([x.get("retrieval_hit_quality") for x in success]), "user_final_modification_rate_on_success": mean_or_none([x.get("user_final_modification_rate") for x in success])}

def save(results, summary):
    DETAIL_JSON.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    with DETAIL_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        cols = ["id", "topic", "mode", "outline_valid", "content_valid", "latency_seconds", "retries_used", "json_valid_rate", "field_completeness_rate", "over_limit_rate", "retrieval_hit_quality", "user_final_modification_rate", "slide_count", "error"]
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for x in results: w.writerow({k: x.get(k, "") for k in cols})

async def run(args):
    data = json.loads(Path(args.dataset).read_text(encoding="utf-8"))
    if args.limit: data = data[:args.limit]
    sem = asyncio.Semaphore(args.concurrency)
    results = await asyncio.gather(*[eval_one(s, sem, args) for s in data])
    summary = agg(results, args); save(results, summary)
    print("评估完成")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(DETAIL_JSON); print(SUMMARY); print(DETAIL_CSV)

def parse_args():
    p = argparse.ArgumentParser(description="TrainPPTAgent 自动评估脚本")
    p.add_argument("--dataset", default=str(DATASET)); p.add_argument("--base-url", default="http://127.0.0.1:6800")
    p.add_argument("--timeout", type=float, default=600.0); p.add_argument("--max-retries", type=int, default=2)
    p.add_argument("--concurrency", type=int, default=1); p.add_argument("--request-interval", type=float, default=0.0)
    p.add_argument("--limit", type=int, default=0); p.add_argument("--mode", choices=["e2e", "slides-only"], default="e2e")
    p.add_argument("--outline-field", default="reference_outline", help="slides-only 模式使用的数据集大纲字段名")
    return p.parse_args()

if __name__ == "__main__": asyncio.run(run(parse_args()))
