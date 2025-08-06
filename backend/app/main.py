from datetime import datetime, timezone
import os
import boto3
from bson import ObjectId
from fastapi import APIRouter, Body, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from botocore.exceptions import BotoCoreError, ClientError
from pymongo import MongoClient

app = FastAPI()

api = APIRouter(prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB setup
mongo_client = MongoClient(os.environ.get("MONGO_URL"))
db = mongo_client["filedb"]
files_collection = db["files"]
files_collection.create_index("filename", unique=True)

# MinIO (S3-compatible) setup
s3 = boto3.client(
    "s3",
    endpoint_url=os.environ.get("MINIO_ENDPOINT"),
    aws_access_key_id=os.environ.get("MINIO_ACCESS_KEY"),
    aws_secret_access_key=os.environ.get("MINIO_SECRET_KEY")
)
BUCKET_NAME = "uploads"

# Ensure bucket exists
try:
    s3.head_bucket(Bucket=BUCKET_NAME)
except ClientError:
    s3.create_bucket(Bucket=BUCKET_NAME)


@api.post("/upload")
def upload_file(file: UploadFile = File(...)):
    if files_collection.find_one({"filename": file.filename}):
        raise HTTPException(status_code=400, detail="File with this filename already exists.")

    try:
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        file.file.seek(0)

        s3.upload_fileobj(file.file, BUCKET_NAME, file.filename)

        doc = {
            "filename": file.filename,
            "s3_path": f"{BUCKET_NAME}/{file.filename}",
            "content_type": file.content_type,
            "upload_date": datetime.now(timezone.utc),
            "size": size
        }
        result = files_collection.insert_one(doc)
        doc["_id"] = str(result.inserted_id)
        doc["upload_date"] = doc["upload_date"].isoformat()
        return doc
    except (BotoCoreError, ClientError) as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@api.get("/files")
def list_files():
    files = list(files_collection.find({}))
    for file in files:
        file["_id"] = str(file["_id"])
        if isinstance(file.get("upload_date"), datetime):
            file["upload_date"] = file["upload_date"].isoformat()
    return files
    

@api.patch("/files/{file_id}")
def rename_file(file_id: str, data: dict = Body(...)):
    new_name = data.get("filename")
    if not new_name:
        raise HTTPException(status_code=400, detail="New filename required")

    file_doc = files_collection.find_one({"_id": ObjectId(file_id)})
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")

    if file_doc["filename"] == new_name:
        return {"message": "Filename is already set to this value"}

    # Rename object in MinIO
    try:
        s3.copy_object(
            Bucket=BUCKET_NAME,
            CopySource=f"{BUCKET_NAME}/{file_doc['filename']}",
            Key=new_name
        )
        s3.delete_object(Bucket=BUCKET_NAME, Key=file_doc["filename"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MinIO rename failed: {e}")

    # Rename object in DB
    files_collection.update_one(
        {"_id": ObjectId(file_id)},
        {"$set": {"filename": new_name, "s3_path": f"{BUCKET_NAME}/{new_name}"}}
    )

    return {"message": "Renamed"}

@api.delete("/files/{file_id}")
def delete_file(file_id: str):
    file = files_collection.find_one({"_id": ObjectId(file_id)})
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        s3.delete_object(Bucket=BUCKET_NAME, Key=file["filename"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    files_collection.delete_one({"_id": ObjectId(file_id)})
    return {"message": "Deleted"}

@api.get("/files/{file_id}/download")
def download_file(file_id: str):
    file = files_collection.find_one({"_id": ObjectId(file_id)})
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': BUCKET_NAME, 'Key': file["filename"]},
        ExpiresIn=60
    )
    return {"url": url}

app.include_router(api)