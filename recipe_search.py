import argparse
import hashlib
import json
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from fastembed import TextEmbedding
from llama_index.core.node_parser import TokenTextSplitter
from qdrant_client import QdrantClient, models


ROOT = Path(__file__).resolve().parent
RECIPES_PATH = ROOT / "data" / "recipes.json"
INDEX_PATH = ROOT / ".recipe-index"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
STRATEGIES = ("tokens", "sections")
PARENT_CHILD = "parent-child"
SEARCH_STRATEGIES = (*STRATEGIES, PARENT_CHILD)


def load_recipes(path=RECIPES_PATH):
    recipes = json.loads(Path(path).read_text(encoding="utf-8"))
    recipe_ids = {recipe["id"] for recipe in recipes}
    if not recipes or len(recipe_ids) != len(recipes):
        raise ValueError("De dataset moet minstens één recept bevatten en elk ID moet uniek zijn.")
    return recipes


def recipe_sections(recipe):
    durations = []
    for cook_time in recipe["cook_times"]:
        minutes = str(cook_time["minutes"])
        if "max_minutes" in cook_time:
            minutes += f"–{cook_time['max_minutes']}"
        setting = f" ({cook_time['setting']})" if "setting" in cook_time else ""
        durations.append(f"{minutes} minuten{setting}")

    ingredients = []
    for item in recipe["ingredients"]:
        line = item["name"]
        if "quantity" in item:
            line = f"{item['quantity']} {item['unit']} {line}"
        if "note" in item:
            line += f" ({item['note']})"
        ingredients.append(line)

    return {
        "Overzicht": (
            f"Porties: {recipe['servings']}. Voorbereiding: {recipe['prep_minutes']} minuten. "
            f"Kooktijd: {' of '.join(durations)}. Dieettags: {', '.join(recipe['dietary_tags'])}."
        ),
        "Ingrediënten": "\n".join(ingredients),
        "Bereiding": "\n".join(f"{i}. {step}" for i, step in enumerate(recipe["instructions"], 1)),
        "Vervangingen": "\n".join(recipe.get("substitutions", [])),
    }


class RecipeSearch:
    def __init__(self, recipes_path=RECIPES_PATH, index_path=INDEX_PATH):
        splitter = TokenTextSplitter(chunk_size=96, chunk_overlap=16, separator="\n")
        self.chunks = {strategy: [] for strategy in SEARCH_STRATEGIES}
        self.parent_sections = {}
        for recipe in load_recipes(recipes_path):
            sections = {name: text for name, text in recipe_sections(recipe).items() if text}
            full_text = "\n\n".join(f"{name}\n{text}" for name, text in sections.items())
            for strategy, blocks in (("tokens", {"Volledige recept": full_text}), ("sections", sections)):
                for label, block in blocks.items():
                    for part in splitter.split_text(block):
                        self.chunks[strategy].append({
                            "recipe_id": recipe["id"],
                            "title": recipe["title"],
                            "source_url": recipe["source_url"],
                            "section": label,
                            "text": f"{recipe['title']} | {label}\n{part}",
                        })
            for label, block in sections.items():
                parent_id = f"{recipe['id']}/{label}"
                heading = f"{recipe['title']} | {label}\n"
                self.parent_sections[parent_id] = heading + block
                for line in block.splitlines():
                    for part in splitter.split_text(line):
                        self.chunks[PARENT_CHILD].append({
                            "recipe_id": recipe["id"],
                            "title": recipe["title"],
                            "source_url": recipe["source_url"],
                            "section": label,
                            "parent_id": parent_id,
                            "text": heading + part,
                        })

        self.client = QdrantClient(path=str(index_path))
        self.embedding = None

    def close(self):
        self.client.close()

    def collection_name(self, strategy):
        index_contents = json.dumps([MODEL_NAME, self.chunks[strategy]], sort_keys=True)
        digest = hashlib.sha256(index_contents.encode()).hexdigest()[:16]
        return f"recipes_{strategy}_{digest}"

    def model(self):
        if self.embedding is None:
            self.embedding = TextEmbedding(model_name=MODEL_NAME, threads=2)
        return self.embedding

    def is_built(self, strategy):
        name = self.collection_name(strategy)
        return (
            self.client.collection_exists(name)
            and self.client.count(name, exact=True).count == len(self.chunks[strategy])
        )

    def build(self, strategy):
        chunks = self.chunks[strategy]
        if self.is_built(strategy):
            return len(chunks)

        name = self.collection_name(strategy)
        vectors = [vector.tolist() for vector in self.model().embed(chunk["text"] for chunk in chunks)]
        if not self.client.collection_exists(name):
            self.client.create_collection(
                name, vectors_config=models.VectorParams(size=len(vectors[0]), distance=models.Distance.COSINE)
            )
        self.client.upsert(name, points=[
            models.PointStruct(id=str(uuid5(NAMESPACE_URL, f"{name}/{i}")), vector=vector, payload=chunk)
            for i, (chunk, vector) in enumerate(zip(chunks, vectors, strict=True))
        ])
        return len(chunks)

    def search(self, question, strategy="sections", top_k=3, recipe_id=None):
        if not question.strip() or top_k < 1:
            raise ValueError("Geef een vraag op en kies minstens één resultaat.")
        if not self.is_built(strategy):
            raise ValueError("De index voor deze dataset ontbreekt. Voer eerst 'python recipe_search.py build' uit.")

        recipe_filter = None
        if recipe_id is not None:
            recipe_filter = models.Filter(must=[
                models.FieldCondition(key="recipe_id", match=models.MatchValue(value=recipe_id))
            ])
        name = self.collection_name(strategy)
        vector = next(self.model().query_embed(question)).tolist()
        if strategy == PARENT_CHILD:
            groups = self.client.query_points_groups(
                name, query=vector, group_by="parent_id", group_size=1,
                limit=top_k, query_filter=recipe_filter, with_payload=True,
            ).groups
            hits = []
            for group in groups:
                child = group.hits[0]
                payload = child.payload
                hits.append({
                    **payload,
                    "score": child.score,
                    "matched_child": payload["text"],
                    "text": self.parent_sections[payload["parent_id"]],
                })
            return hits

        results = self.client.query_points(
            name,
            query=vector,
            limit=top_k,
            with_payload=True,
            query_filter=recipe_filter,
        )
        return [{**point.payload, "score": point.score} for point in results.points]


def main():
    parser = argparse.ArgumentParser(description="Bouw en vergelijk lokale receptenindexen.")
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="Indexeer de recepten.")
    build.add_argument("--strategy", choices=(*SEARCH_STRATEGIES, "both"), default="both")
    search = commands.add_parser("search", help="Toon de meest relevante tekstfragmenten.")
    search.add_argument("question")
    search.add_argument("--strategy", choices=(*SEARCH_STRATEGIES, "both"), default="both")
    search.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()

    store = RecipeSearch()
    try:
        strategies = STRATEGIES if args.strategy == "both" else (args.strategy,)
        if args.command == "build":
            for strategy in strategies:
                print(f"{strategy}: {store.build(strategy)} chunks in de lokale vectorstore")
            return

        for strategy in strategies:
            print(f"\n{strategy}")
            for rank, hit in enumerate(store.search(args.question, strategy, args.top_k), 1):
                if "matched_child" in hit:
                    print(f"\nGevonden deel: {hit['matched_child']}")
                print(f"\n{rank}. [{hit['score']:.3f}] {hit['text']}\nBron: {hit['source_url']}")
    except ValueError as exc:
        parser.error(str(exc))
    finally:
        store.close()


if __name__ == "__main__":
    main()
