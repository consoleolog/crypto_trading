from contextlib import asynccontextmanager

from fastapi import FastAPI, BackgroundTasks

def run_trading():
    pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    background_tasks = BackgroundTasks()
    background_tasks.add_task(run_trading)

    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "FastAPI server is running"}