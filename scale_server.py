from decimal import Decimal
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, StringConstraints


Servings = Annotated[int, Field(gt=0, strict=True)]
NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class Ingredient(BaseModel):
    name: NonEmptyText
    quantity: Annotated[Decimal, Field(ge=0, allow_inf_nan=False)] | None = None
    unit: NonEmptyText | None = None
    note: str | None = None


class ScaleResult(BaseModel):
    from_servings: Servings
    to_servings: Servings
    ingredients: list[Ingredient]


server = FastMCP("Flavor Chef", log_level="WARNING")


@server.tool()
def scale_ingredients(
    from_servings: Servings,
    to_servings: Servings,
    ingredients: Annotated[list[Ingredient], Field(min_length=1)],
) -> ScaleResult:
    """Scale ingredient quantities to a new serving count, preserving units and unmeasured items."""
    scaled = []
    for ingredient in ingredients:
        quantity = ingredient.quantity
        if quantity is not None:
            quantity = quantity * to_servings / from_servings
        scaled.append(ingredient.model_copy(update={"quantity": quantity}))
    return ScaleResult(from_servings=from_servings, to_servings=to_servings, ingredients=scaled)


if __name__ == "__main__":
    server.run(transport="stdio")
