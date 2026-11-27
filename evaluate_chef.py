import argparse
import asyncio
import json
import math
import os
import re
from collections import Counter
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from statistics import mean, median

import httpx

from chef_agent import build_agent, groq_client, invoke_agent
from recipe_search import MODEL_NAME, RECIPES_PATH, ROOT, STRATEGIES


CASES = ROOT / "data" / "evaluation.json"
GROQ_URL = "https://api.groq.com/openai/v1/"


class GroqBenchmarkTransport(httpx.AsyncHTTPTransport):
    async def handle_async_request(self, request):
        for attempt in range(4):
            response = await super().handle_async_request(request)
            if response.status_code != 429 or attempt == 3:
                return response

            try:
                delay = float(response.headers.get("retry-after", ""))
            except ValueError:
                return response
            if not 0 <= delay <= 120:
                return response

            await response.aclose()
            print(f"Groq-limiet bereikt. Nieuwe poging over {math.ceil(delay) + 1} s.", flush=True)
            await asyncio.sleep(delay + 1)


def contains(text, phrase):
    text = " ".join(text.casefold().split())
    return re.search(rf"(?<![\w.,]){re.escape(phrase.casefold())}(?!\w)", text) is not None


def evidence_rank(case, hits):
    seen = []
    for rank, hit in enumerate(hits, 1):
        if hit["recipe_id"] == case["recipe_id"]:
            seen.append(hit["text"])
        if all(any(contains(text, phrase) for text in seen for phrase in group) for group in case["evidence"]):
            return rank
    return None


def tool_answer_matches(expected, actual):
    if not actual or any(actual[field] != expected[field] for field in ("from_servings", "to_servings")):
        return False
    quantities = {(item["name"], item["unit"]): Decimal(item["quantity"])
                  for item in actual["ingredients"] if item["quantity"] is not None}
    return all(quantities.get((item["name"], item["unit"])) == Decimal(item["quantity"])
               for item in expected["ingredients"])


def failure_stage(case, row):
    if not row["route_ok"]:
        return "routing"
    if case["route"] == "chat" and (row["retrieved"] or row["tool_result"] is not None):
        return "routing"
    if "evidence" in case and row["evidence_rank"] is None:
        return "retrieval"
    if case.get("expected_missing_information") and not any(
        hit["recipe_id"] == case["recipe_id"] for hit in row["retrieved"]
    ):
        return "retrieval"
    if case["route"] == "scale_recipe":
        hits = row["retrieved"]
        if not hits or hits[0]["recipe_id"] != case["recipe_id"]:
            return "retrieval"
    if row.get("tool_ok") is False:
        return "calculation"
    if not (row["answer"] or "").strip():
        return "answer"
    return None


async def score_ragas(metrics, case, state):
    inputs = {
        "user_input": case["question"],
        "retrieved_contexts": [hit["text"] for hit in state.get("hits", [])],
    }
    if state["route"] != case["route"] or not inputs["retrieved_contexts"]:
        return dict.fromkeys(metrics)

    scores = {}
    for name, metric in metrics.items():
        if name == "faithfulness":
            response = (state.get("answer") or "").partition("\n\nBronnen\n")[0].strip()
            if not response:
                scores[name] = None
                continue
            extra = {"response": response}
        else:
            extra = {"reference": case["reference"]}
        value = float((await metric.ascore(**inputs, **extra)).value)
        scores[name] = round(value, 4) if math.isfinite(value) else None
    return scores


async def evaluate(cases, strategy, groq=None, metrics=None):
    agent = build_agent(groq, strategy=strategy)
    rows = []
    for case in cases:
        state = await invoke_agent(agent, case["question"])
        hits = state.get("hits", [])
        row = {
            "id": case["id"],
            "question": case["question"],
            "reference": case["reference"],
            "expected_route": case["route"],
            "actual_route": state["route"],
            "route_ok": case["route"] == state["route"],
            "retrieved": [
                {"recipe_id": hit["recipe_id"], "section": hit["section"],
                 "source_url": hit["source_url"], "score": round(hit["score"], 4)}
                for hit in hits
            ],
            "retrieved_text": [hit["text"] for hit in hits],
            "tool_result": state.get("tool_result"),
            "answer": state.get("answer"),
            "trace": state["trace"],
            "latency_ms": state["latency_ms"],
            "llm_calls": state["llm_calls"],
        }
        if "recipe_id" in case:
            row["expected_recipe_id"] = case["recipe_id"]
        if case.get("expected_missing_information"):
            row["expected_missing_information"] = True
        if "evidence" in case:
            row["expected_evidence"] = case["evidence"]
            row["evidence_rank"] = evidence_rank(case, hits)
            if metrics:
                row["ragas"] = await score_ragas(metrics, case, state)
        if "tool" in case:
            row["expected_tool"] = case["tool"]
            row["tool_ok"] = tool_answer_matches(case["tool"], row["tool_result"])
        row["failure_stage"] = failure_stage(case, row)
        rows.append(row)

    retrieval = [row["evidence_rank"] for row in rows if "evidence_rank" in row]
    tools = [row["tool_ok"] for row in rows if "tool_ok" in row]
    summary = {
        "routes_correct": sum(row["route_ok"] for row in rows),
        "routes_total": len(rows),
        "evidence_at_1": retrieval.count(1),
        "evidence_at_3": sum(rank is not None for rank in retrieval),
        "retrieval_total": len(retrieval),
        "mean_reciprocal_evidence_rank": round(mean(1 / rank if rank else 0 for rank in retrieval), 4),
        "tools_correct": sum(tools),
        "tools_total": len(tools),
        "median_latency_ms": round(median(row["latency_ms"] for row in rows), 2),
        "failures_by_stage": dict(Counter(row["failure_stage"] for row in rows if row["failure_stage"])),
    }
    if metrics:
        summary["ragas"] = {}
        for name in metrics:
            scores = [row.get("ragas", {}).get(name) for row in rows]
            scores = [score for score in scores if score is not None]
            summary["ragas"][name] = {
                "mean": round(mean(scores), 4) if scores else None,
                "scored": len(scores),
                "total": len(retrieval),
            }
    return {"summary": summary, "cases": rows}


async def benchmark(api_key):
    case_data = CASES.read_bytes()
    cases = json.loads(case_data)
    report = {
        "mode": "groq_ragas" if api_key else "local",
        "ragas_executed": bool(api_key),
        "embedding_model": MODEL_NAME,
        "recipes_sha256": sha256(RECIPES_PATH.read_bytes()).hexdigest(),
        "evaluation_sha256": sha256(case_data).hexdigest(),
        "strategies": {},
    }
    if not api_key:
        for strategy in STRATEGIES:
            print(f"Lokale benchmark: {strategy}", flush=True)
            report["strategies"][strategy] = await evaluate(cases, strategy)
        return report

    from openai import AsyncOpenAI
    from ragas.llms import llm_factory
    from ragas.metrics.collections import ContextPrecision, ContextRecall, Faithfulness

    judge_model = os.environ.get("RAGAS_JUDGE_MODEL", "openai/gpt-oss-120b")
    report["judge_model"] = judge_model
    judge_http = httpx.AsyncClient(transport=GroqBenchmarkTransport())
    async with (
        AsyncOpenAI(base_url=GROQ_URL, api_key=api_key, timeout=60, http_client=judge_http) as judge,
        groq_client(api_key, transport=GroqBenchmarkTransport()) as agent_client,
    ):
        llm = llm_factory(judge_model, client=judge, temperature=0)
        metrics = {
            "context_precision": ContextPrecision(llm=llm),
            "context_recall": ContextRecall(llm=llm),
            "faithfulness": Faithfulness(llm=llm),
        }
        for strategy in STRATEGIES:
            print(f"Ragas-benchmark: {strategy}", flush=True)
            report["strategies"][strategy] = await evaluate(cases, strategy, agent_client, metrics)
    return report


def main():
    parser = argparse.ArgumentParser(description="Vergelijk chunkmethodes, routering en MCP-uitkomsten.")
    parser.add_argument("--ragas", action="store_true", help="Gebruik Groq voor generatie en evaluatie met Ragas.")
    parser.add_argument("--output", type=Path, help="Schrijf de resultaten per vraag naar dit JSON-bestand.")
    args = parser.parse_args()
    key = os.environ.get("GROQ_API_KEY") if args.ragas else None
    if args.ragas and not key:
        parser.error("Stel GROQ_API_KEY in om --ragas te gebruiken.")
    report = asyncio.run(benchmark(key))
    for strategy, results in report["strategies"].items():
        print(f"{strategy}: {json.dumps(results['summary'])}")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
