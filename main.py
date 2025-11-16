from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv
load_dotenv()   

MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI) 
db = client["GenAPIDB"];
genApi_data = db["GenAPIDB_Coll"]
app = FastAPI()

class genapidata(BaseModel):
    name: str
    phone: int
    city: str   
    course: str
    
    
@app.post("/genapi/insert")
async def genApi_insert_data(data: genapidata):
    result = await genApi_data.insert_one(data.dict())  
    return str(result.inserted_id)

        
        
def to_dict(document: dict) -> dict:
    document["id"] = str(document["_id"])
    del document["_id"]
    return document


@app.get("/genapi/showdata")
async def show_genapi_data():
    items = []
    cursor = genApi_data.find({})  # fetch all documents

    async for document in cursor:
        items.append(to_dict(document))   # convert Mongo document → JSON-friendly

    return items


@app.put("/genapi/update/{id}")
async def update_full_row(id: str, data: genapidata):
    
    oid = ObjectId(id)
    result = await genApi_data.update_one(
        {"_id": oid},
        {"$set": data.dict()}
    )
    

@app.patch("/genapi/update/{id}")
async def partial_update(id: str, payload: dict):
    try:
        oid = ObjectId(id)
    except:
        raise HTTPException(400, "Invalid ID")

    if not payload:
        raise HTTPException(400, "Empty update payload")

    # Do not allow _id modification
    payload.pop("_id", None)

    result = await genApi_data.update_one(
        {"_id": oid},
        {"$set": payload}
    )

    if result.matched_count == 0:
        raise HTTPException(404, "Record not found")

    return {"message": "Partial update successful"}

    


@app.delete("/genapi/delete/{id}")
async def delete_by_id(id: str):
    # Validate ObjectId
    try:
        oid = ObjectId(id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    # Perform delete
    result = await genApi_data.delete_one({"_id": oid})

    # Check if record existed
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Record not found")

    return {"message": "Record deleted successfully"}