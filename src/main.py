from fastapi import FastAPI

app = FastAPI()


@app.get("/GetRead")
def GetRead():
    return {"msg": "Hello World"}
