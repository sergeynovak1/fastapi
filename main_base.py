from typing import Optional, List, Set, Dict
from datetime import datetime, time, timedelta
from uuid import UUID
from fastapi import FastAPI, Path, Query, Body, Cookie, Header, status, Form, UploadFile, File, Request, Depends, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum

app = FastAPI()


class Image(BaseModel):
    url: HttpUrl
    name: str = Field(..., example="Foo")


class Item(BaseModel):
    name: str
    description: Optional[str] = Field(
        None, title="The description of the item", max_length=300
    )
    price: float = Field(..., gt=0, description="The price must be greater than zero")
    tax: Optional[float] = None
    tags: Set[str] = set()
    images: Optional[List[Image]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "item1",
                "description": "description1",
                "price": 1,
                "tax": 0,
                "tags": ['tag1'],
                "images": [
                    {
                        "url": "https://example1.com/",
                        "name": "string"
                    }
                ]
            }
        }


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


@app.put("/items1/{item_id}")
async def read_items(
        item_id: UUID,
        start_datetime: Optional[datetime] = Body(None),
        end_datetime: Optional[datetime] = Body(None),
        repeat_at: Optional[time] = Body(None),
        process_after: Optional[timedelta] = Body(None),
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "repeat_at": repeat_at,
        "process_after": process_after,
        "start_process": start_process,
        "duration": duration,
    }


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


@app.get("/items1/")
async def read_items1(ads_id: Optional[str] = Cookie(None)):
    return {"ads_id": ads_id}


@app.get("/items2/")
async def read_items2(user_agent: Optional[str] = Header(None)):
    return {"User-Agent": user_agent}


@app.post("/items/", response_model=Item, response_model_exclude_unset=True, response_model_exclude={"name"},
          status_code=status.HTTP_201_CREATED, summary="Create an item",
          # description="Create an item with all the information, name, description, price, tax and a set of unique tags",
          tags=['create'],
          response_description="The created item",
          deprecated=True)
async def create_item(item: Item):
    """
    Create an item with all the information:

    - **name**: each item must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this item
    """
    return item


@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}


@app.post("/files/")
async def create_file(file: bytes = File(...)):
    return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    return {"filename": file.filename}


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )


@app.get("/unicorns/{name}")
async def read_unicorn(name: str):
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}

items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}


class Item2(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    tax: float = 10.5
    tags: List[str] = []


@app.put("/items2/{item_id}", response_model=Item2)
async def update_item(item_id: str, item: Item2):
    update_item_encoded = jsonable_encoder(item)
    items[item_id] = update_item_encoded
    return update_item_encoded


@app.patch("/items2/{item_id}")
async def update_item(item_id: str, item: Item2):
    stored_item_data = items[item_id]
    stored_item_model = Item2(**stored_item_data)
    update_data = item.dict(exclude_unset=True)
    updated_item = stored_item_model.copy(update=update_data)
    items[item_id] = jsonable_encoder(updated_item)
    return jsonable_encoder(updated_item)


async def common_parameters(q: Optional[str] = None, skip: int = 0, limit: int= 100):
    return {"q": q, "skip": skip, "limit": limit}


@app.get("/users/")
async def read_users(commons: dict = Depends(common_parameters)):
    return commons

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


class CommonQueryParams:
    def __init__(self, q: Optional[str] = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit


@app.get("/items3/")
async def read_items(commons: CommonQueryParams = Depends(CommonQueryParams)):
    response = {}
    if commons.q:
        response.update({"q": commons.q})
        items = fake_items_db[commons.skip : commons.skip + commons.limit]
        response.update({"items": items})
    return response


@app.get("/legacy/")
def get_legacy_data():
    data = """<?xml version="1.0"?>
    <shampoo>
    <Header>
    Apply shampoo here.
    </Header>
    <Body>
    You'll have to use soap here.
    </Body>
    </shampoo>
    """
    return Response(content=data, media_type="application/xml")
