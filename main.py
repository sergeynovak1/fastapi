from typing import Optional, List, Set, Dict
from fastapi import FastAPI, Path, Query, Body
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum

app = FastAPI()


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str
    description: Optional[str] = Field(
        None, title="The description of the item", max_length=300
    )
    price: float = Field(..., gt=0, description="The price must be greater than zero")
    tax: Optional[float] = None
    tags: Set[str] = set()
    images: Optional[List[Image]] = None


class User(BaseModel):
    username: str
    full_name: Optional[str] = None


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(
        item_id: int = Path(..., title="The ID of the item to get"),
        q: Optional[str] = Query(None, alias="item-query"),
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


@app.get("/items/")
async def read_items(
        q: Optional[str] = Query(
        None,
        alias="item-query",
        title="Query string",
        description="Query string for the items to search in the database that have a good match",
        min_length=3,
        max_length=50,
        # regex="^fixedquery$",
        deprecated=True,
        )

):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, user: User, importance: int = Body(...)):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    return results


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    elif model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


@app.get("/items1/{item_id}")
async def read_user_item(item_id: str, needy: str):
    item = {"item_id": item_id, "needy": needy}
    return item


@app.post("/images/multiple/")
async def create_multiple_images(images: List[Image]):
    return images


@app.post("/index-weights/")
async def create_index_weights(weights: Dict[int, float]):
    return weights
