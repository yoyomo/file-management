import os
import boto3
from fastapi import APIRouter, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from botocore.exceptions import BotoCoreError, ClientError
from pymongo import MongoClient

app = FastAPI()

api = APIRouter(prefix="/api/v1")

# CORS: allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict to "http://localhost:3000"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB setup
mongo_client = MongoClient(os.environ.get("MONGO_URL"))
db = mongo_client["filedb"]
files_collection = db["files"]

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
async def upload_file(file: UploadFile = File(...)):
    try:
        s3.upload_fileobj(file.file, BUCKET_NAME, file.filename)

        files_collection.insert_one({
            "filename": file.filename,
            "s3_path": f"{BUCKET_NAME}/{file.filename}",
            "content_type": file.content_type
        })

        return {"message": "Upload successful", "file": file.filename}
    except (BotoCoreError, ClientError) as e:
        raise HTTPException(status_code=500, detail=str(e))
    
app.include_router(api)