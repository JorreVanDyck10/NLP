import argparse
import asyncio
import json
import math
import os
import re
from collections import Counter
from contextlib import nullcontext
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from statistics import mean, median

import httpx

from chef_agent import McpToolError, build_agent, groq_client, invoke_agent
from recipe_search import MODEL_NAME, RECIPES_PATH, ROOT, STRATEGIES


CASES = ROOT / "data" / "evaluation.json"
GROQ_URL = "https://api.groq.com/openai/v1/"
OLLAMA_URL = "http://127.0.0.1:11434/v1/"
OLLAMA_JUDGE = "qwen3.5:4b-q4_K_M"


class GroqBenchmarkTransport(httpx.AsyncHTTPTransport):
    blocked_retry_after: float | None = None

    async def handle_async_request(self, request):
        for attempt in range(4):
            response = await super().handle_async_request(request)
            if response.status_code != 429:
                return response

            try:
                delay = float(response.headers.get("retry-after", ""))
            except ValueError:
                return response
            if not math.isfinite(delay) or delay < 0:
                return response
            if delay > 120 or attempt == 3:
                self.blocked_retry_after = delay
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
    if not actual:
        return False
    if "amount" in expected:
        return (actual.get("unit") == expected["unit"] and "amount" in actual
                and Decimal(actual["amount"]) == Decimal(expected["amount"]))
    if any(actual.get(field) != expected[field] for field in ("from_servings", "to_servings")):
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
    if row.get("execution_error"):
        return row["execution_error"]["stage"]
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
    if row.get("answer_ok") is False or not (row["answer"] or "").strip():
        return "answer"
    return None


async def score_ragas(metrics, row):
    inputs = {
        "user_input": row["question"],
        "retrieved_contexts": row["retrieved_text"],
    }
    if not row["route_ok"] or not inputs["retrieved_contexts"]:
        return dict.fromkeys(metrics), {}

    scores = {}
    errors = {}
    for name, metric in metrics.items():
        if name == "faithfulness":
            response = (row["answer"] or "").partition("\n\nBronnen\n")[0].strip()
            if not response:
                scores[name] = None
                continue
            extra = {"response": response}
        else:
            extra = {"reference": row["reference"]}
        try:
            value = float((await metric.ascore(**inputs, **extra)).value)
            scores[name] = round(value, 4) if math.isfinite(value) else None
        except Exception as exc:
            scores[name] = None
            errors[name] = type(exc).__name__
    return scores, errors


def ragas_summary(rows, metric_names):
    summary = {}
    for name in metric_names:
        scores = [row.get("ragas", {}).get(name) for row in rows]
        scores = [score for score in scores if score is not None]
        summary[name] = {"mean": round(mean(scores), 4) if scores else None, "scored": len(scores),
                         "total": sum("evidence_rank" in row for row in rows)}
    return summary


async def evaluate(cases, strategy, groq=None, metrics=None):
    agent = build_agent(groq, strategy=strategy)
    rows = []
    for case in cases:
        partial = {}
        execution_error = None
        try:
            state = await invoke_agent(agent, case["question"], on_update=partial.update)
        except (httpx.HTTPError, OSError, RuntimeError, ValueError) as exc:
            state = partial
            route = state.get("route")
            if isinstance(exc, McpToolError):
                stage = "calculation"
            elif route is None:
                stage = "routing"
            elif route in {"search", "scale_recipe"} and "hits" not in state:
                stage = "retrieval"
            else:
                stage = "answer"
            execution_error = {"stage": stage, "type": type(exc).__name__}
            if isinstance(exc, httpx.HTTPStatusError):
                execution_error["status"] = exc.response.status_code
        hits = state.get("hits", [])
        row = {
            "id": case["id"],
            "question": case["question"],
            "reference": case["reference"],
            "expected_route": case["route"],
            "actual_route": state.get("route"),
            "route_ok": case["route"] == state.get("route"),
            "retrieved": [
                {"recipe_id": hit["recipe_id"], "section": hit["section"],
                 "source_url": hit["source_url"], "score": round(hit["score"], 4)}
                for hit in hits
            ],
            "retrieved_text": [hit["text"] for hit in hits],
            "tool_result": state.get("tool_result"),
            "answer": state.get("answer"),
            "trace": state.get("trace", []),
            "latency_ms": state.get("latency_ms") if execution_error is None else None,
            "llm_calls": state.get("llm_calls", []),
        }
        if execution_error:
            row["execution_error"] = execution_error
        if "recipe_id" in case:
            row["expected_recipe_id"] = case["recipe_id"]
        if case.get("expected_missing_information"):
            row["expected_missing_information"] = True
        if "evidence" in case:
            row["expected_evidence"] = case["evidence"]
            row["evidence_rank"] = evidence_rank(case, hits)
            if metrics:
                scores, errors = await score_ragas(metrics, row)
                row["ragas"] = scores
                if errors:
                    row["ragas_errors"] = errors
        if "tool" in case:
            row["expected_tool"] = case["tool"]
            row["tool_ok"] = tool_answer_matches(case["tool"], row["tool_result"])
        if groq and "answer_contains" in case:
            answer = (row["answer"] or "").partition("\n\nBronnen\n")[0]
            row["answer_ok"] = all(any(contains(answer, phrase) for phrase in group)
                                   for group in case["answer_contains"])
        row["failure_stage"] = failure_stage(case, row)
        rows.append(row)

    retrieval = [row["evidence_rank"] for row in rows if "evidence_rank" in row]
    tools = [row["tool_ok"] for row in rows if "tool_ok" in row]
    latencies = [row["latency_ms"] for row in rows if row["latency_ms"] is not None]
    summary = {
        "routes_correct": sum(row["route_ok"] for row in rows),
        "routes_total": len(rows),
        "evidence_at_1": retrieval.count(1),
        "evidence_at_3": sum(rank is not None for rank in retrieval),
        "retrieval_total": len(retrieval),
        "mean_reciprocal_evidence_rank": round(mean(1 / rank if rank else 0 for rank in retrieval), 4) if retrieval else None,
        "tools_correct": sum(tools),
        "tools_total": len(tools),
        "median_latency_ms": round(median(latencies), 2) if latencies else None,
        "execution_errors": sum("execution_error" in row for row in rows),
        "failures_by_stage": dict(Counter(row["failure_stage"] for row in rows if row["failure_stage"])),
    }
    if groq:
        calls = [call for row in rows for call in row["llm_calls"]]
        for field in ("prompt_tokens", "completion_tokens"):
            values = [call[field] for call in calls if call.get(field) is not None]
            summary[field] = {"total": sum(values) if values else None, "measured_calls": len(values)}
        ttft = [call["ttft_ms"] for call in calls if call.get("ttft_ms") is not None]
        summary["answer_ttft"] = {"median_ms": round(median(ttft), 2) if ttft else None, "measured_calls": len(ttft)}
    if metrics:
        summary["ragas"] = ragas_summary(rows, metrics)
    return {"summary": summary, "cases": rows}


def make_ragas_metrics(judge_model, judge, **model_settings):
    from ragas.llms import llm_factory
    from ragas.metrics.collections import ContextPrecision, ContextRecall, Faithfulness

    llm = llm_factory(judge_model, client=judge, temperature=0, **model_settings)
    return {"context_precision": ContextPrecision(llm=llm), "context_recall": ContextRecall(llm=llm),
            "faithfulness": Faithfulness(llm=llm)}


def write_report(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


async def score_existing_report(report, api_key, output, *, local_judge=False):
    from openai import AsyncOpenAI

    judge_provider = "ollama" if local_judge else "groq"
    judge_model = os.environ.get("RAGAS_JUDGE_MODEL", OLLAMA_JUDGE if local_judge else "openai/gpt-oss-120b")
    if (not isinstance(report, dict) or report.get("mode") not in {"groq", "groq_ragas"}
            or report.get("recipes_sha256") != sha256(RECIPES_PATH.read_bytes()).hexdigest()
            or report.get("evaluation_sha256") != sha256(CASES.read_bytes()).hexdigest()
            or report.get("embedding_model") != MODEL_NAME):
        raise ValueError("Gebruik een Groq-rapport van de huidige dataset, vragen en embeddinginstellingen.")
    if "judge_model" in report and (report["judge_model"] != judge_model
                                    or report.get("judge_provider", "groq") != judge_provider):
        raise ValueError("Gebruik dezelfde Ragas-beoordelaar als in het bestaande rapport.")

    strategies = [report["strategies"][strategy] for strategy in STRATEGIES]
    cases = json.loads(CASES.read_bytes())
    if "case_ids" in report:
        cases = [case for case in cases if case["id"] in report["case_ids"]]
    fields = ("id", "question", "reference")
    expected = [tuple(case[field] for field in fields) + (case["route"],) for case in cases]
    if not expected or any(
        [tuple(row[field] for field in fields) + (row["expected_route"],) for row in result["cases"]] != expected
        or result["summary"]["execution_errors"] for result in strategies
    ):
        raise ValueError("Gebruik een afgerond Groq-rapport met beide chunkmethodes en zonder uitvoeringsfouten.")

    transport = None if local_judge else GroqBenchmarkTransport()
    judge_http = httpx.AsyncClient(transport=transport)
    endpoint = OLLAMA_URL if local_judge else GROQ_URL
    model_settings = {"reasoning_effort": "none"} if local_judge else {}
    async with AsyncOpenAI(base_url=endpoint, api_key="ollama" if local_judge else api_key,
                           timeout=120 if local_judge else 60, max_retries=0, http_client=judge_http) as judge:
        metrics = make_ragas_metrics(judge_model, judge, **model_settings)
        report.update(mode="groq_ragas", ragas_executed=True,
                      judge_model=judge_model, judge_provider=judge_provider)
        for result in strategies:
            result["summary"]["ragas"] = ragas_summary(result["cases"], metrics)
        write_report(output, report)

        # Score both chunk methods per question so a quota interruption preserves matched pairs.
        for pair in zip(*(result["cases"] for result in strategies), strict=True):
            for strategy, result, row in zip(STRATEGIES, strategies, pair, strict=True):
                if "evidence_rank" not in row or not row["route_ok"] or not row["retrieved_text"]:
                    continue
                scores = row.setdefault("ragas", {})
                pending = {name: metric for name, metric in metrics.items() if scores.get(name) is None}
                if not pending:
                    continue
                print(f"Ragas: {strategy} / {row['id']} ({len(pending)} metrieken)", flush=True)
                values, errors = await score_ragas(pending, row)
                scores.update(values)
                previous_errors = row.get("ragas_errors", {})
                remaining_errors = {name: error for name, error in previous_errors.items() if name not in pending}
                remaining_errors.update(errors)
                if remaining_errors:
                    row["ragas_errors"] = remaining_errors
                else:
                    row.pop("ragas_errors", None)
                result["summary"]["ragas"] = ragas_summary(result["cases"], metrics)
                write_report(output, report)
                if transport is not None and transport.blocked_retry_after is not None:
                    print(f"Groq beperkt verdere beoordeling. Probeer opnieuw over {math.ceil(transport.blocked_retry_after)} s.")
                    return report
    return report


async def benchmark(api_key, *, with_ragas=True, case_ids=None):
    case_data = CASES.read_bytes()
    cases = json.loads(case_data)
    if case_ids:
        cases = [case for case in cases if case["id"] in case_ids]
    with_ragas = bool(api_key and with_ragas)
    report = {
        "mode": "groq_ragas" if with_ragas else "groq" if api_key else "local",
        "ragas_executed": with_ragas,
        "embedding_model": MODEL_NAME,
        "recipes_sha256": sha256(RECIPES_PATH.read_bytes()).hexdigest(),
        "evaluation_sha256": sha256(case_data).hexdigest(),
        "strategies": {},
    }
    if case_ids:
        report["case_ids"] = [case["id"] for case in cases]
    if api_key:
        report["agent_model"] = os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")
    if not with_ragas:
        client_context = groq_client(api_key, transport=GroqBenchmarkTransport()) if api_key else nullcontext()
        async with client_context as client:
            for strategy in STRATEGIES:
                print(f"{'Groq' if api_key else 'Lokale'} benchmark: {strategy}", flush=True)
                report["strategies"][strategy] = await evaluate(cases, strategy, client)
        return report

    from openai import AsyncOpenAI
    judge_model = os.environ.get("RAGAS_JUDGE_MODEL", "openai/gpt-oss-120b")
    report["judge_model"] = judge_model
    judge_http = httpx.AsyncClient(transport=GroqBenchmarkTransport())
    async with (
        AsyncOpenAI(base_url=GROQ_URL, api_key=api_key, timeout=60, http_client=judge_http) as judge,
        groq_client(api_key, transport=GroqBenchmarkTransport()) as agent_client,
    ):
        metrics = make_ragas_metrics(judge_model, judge)
        for strategy in STRATEGIES:
            print(f"Ragas-benchmark: {strategy}", flush=True)
            report["strategies"][strategy] = await evaluate(cases, strategy, agent_client, metrics)
    return report


def main():
    parser = argparse.ArgumentParser(description="Vergelijk chunkmethodes, routering en MCP-uitkomsten.")
    live = parser.add_mutually_exclusive_group()
    live.add_argument("--ragas", action="store_true", help="Gebruik Groq voor generatie en evaluatie met Ragas.")
    live.add_argument("--groq", action="store_true", help="Gebruik Groq alleen voor de agent.")
    live.add_argument("--score-report", type=Path, help="Scoor ontbrekende Ragas-metrieken in een bestaande Groq-meting.")
    parser.add_argument("--ollama-judge", action="store_true", help="Gebruik bij --score-report de lokale Ollama-beoordelaar.")
    parser.add_argument("--case", action="append", choices=[case["id"] for case in json.loads(CASES.read_bytes())],
                        help="Draai alleen deze vraag. Mag herhaald worden.")
    parser.add_argument("--output", type=Path, help="Schrijf de resultaten per vraag naar dit JSON-bestand.")
    args = parser.parse_args()
    if args.ollama_judge and not args.score_report:
        parser.error("Gebruik --ollama-judge samen met --score-report.")
    live_mode = args.ragas or args.groq or (args.score_report and not args.ollama_judge)
    key = os.environ.get("GROQ_API_KEY") if live_mode else None
    if live_mode and not key:
        parser.error("Stel GROQ_API_KEY in voor een live benchmark.")
    if args.score_report:
        if not args.output or args.case:
            parser.error("Gebruik --score-report met --output. De invoer bepaalt de vragen.")
        try:
            source_report = json.loads(args.score_report.read_bytes())
            report = asyncio.run(score_existing_report(source_report, key, args.output, local_judge=args.ollama_judge))
        except (OSError, ValueError, KeyError, TypeError) as exc:
            parser.error(str(exc))
    else:
        report = asyncio.run(benchmark(key, with_ragas=args.ragas, case_ids=args.case))
        if args.output:
            write_report(args.output, report)
    for strategy, results in report["strategies"].items():
        print(f"{strategy}: {json.dumps(results['summary'])}")
    if any(results["summary"]["execution_errors"] for results in report["strategies"].values()):
        raise SystemExit(1)
    if args.score_report and any(score["scored"] < score["total"]
                                 for result in report["strategies"].values()
                                 for score in result["summary"]["ragas"].values()):
        print("Ragas-dekking is onvolledig. Gebruik het uitvoerbestand als invoer om te hervatten.")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
