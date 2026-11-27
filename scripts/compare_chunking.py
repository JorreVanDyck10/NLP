"""Vergelijk chunkmethodes op dezelfde vragen, zonder receptfilter."""

import argparse
import json
from pathlib import Path
from statistics import mean, median
from time import perf_counter

from evaluate_chef import CASES, evidence_rank
from recipe_search import ROOT, SEARCH_STRATEGIES, STRATEGIES, RecipeSearch


def compare(store, cases, strategy):
    results = []
    store.search(cases[0]["question"], strategy=strategy)
    for case in cases:
        timings = []
        for _ in range(3):
            start = perf_counter()
            top_3 = store.search(case["question"], strategy=strategy)
            timings.append((perf_counter() - start) * 1000)
        rank = evidence_rank(case, top_3)
        diagnostic_rank = rank if rank is not None else evidence_rank(
            case, store.search(case["question"], strategy=strategy, top_k=10)
        )
        results.append({
            "id": case["id"],
            "question": case["question"],
            "evidence_rank": diagnostic_rank,
            "top_3_evidence_rank": rank,
            "top_3": top_3,
            "context_characters": len("\n\n".join(hit["text"] for hit in top_3)),
            "median_search_ms": round(median(timings), 2),
        })
    ranks = [row["top_3_evidence_rank"] for row in results]
    return {
        "chunks": len(store.chunks[strategy]),
        "questions": len(cases),
        "evidence_at_1": ranks.count(1),
        "evidence_at_3": sum(rank is not None for rank in ranks),
        "mean_context_characters": round(mean(row["context_characters"] for row in results)),
        "median_search_ms": round(median(row["median_search_ms"] for row in results), 2),
        "cases": results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optioneel JSON-bestand met de zoekresultaten.")
    parser.add_argument("--parent-child", action="store_true", help="Vergelijk drie methodes op twee vraagsets.")
    args = parser.parse_args()

    cases = [case for case in json.loads(CASES.read_text(encoding="utf-8")) if "evidence" in case]
    cases += json.loads((ROOT / "data" / "retrieval_checks.json").read_text(encoding="utf-8"))
    store = RecipeSearch()
    try:
        if args.parent_child:
            multi_step = json.loads((ROOT / "data" / "parent_child_checks.json").read_text(encoding="utf-8"))
            report = {label: {strategy: compare(store, questions, strategy) for strategy in SEARCH_STRATEGIES}
                      for label, questions in (("bestaand", cases), ("meerdere_stappen", multi_step))}
        else:
            report = {strategy: compare(store, cases, strategy) for strategy in STRATEGIES}
    finally:
        store.close()

    for label, results in (report.items() if args.parent_child else (("bestaand", report),)):
        for strategy, result in results.items():
            print(f"{label} {strategy}: {result['chunks']} chunks, "
                  f"plek 1 {result['evidence_at_1']}/{result['questions']}, "
                  f"top 3 {result['evidence_at_3']}/{result['questions']}, "
                  f"{result['mean_context_characters']} tekens, {result['median_search_ms']:.2f} ms")
    if args.output:
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
