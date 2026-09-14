from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI!"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}

@app.get("/hello")
async def get_hello():
    return {"message": "Hello, fastapi"}

@app.get("/book/{book_id}")
async def read_book(book_id: int):
    return {"book_id": f"这是第{book_id}本书"}