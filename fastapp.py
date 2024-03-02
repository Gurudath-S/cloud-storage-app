from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import boto3
from botocore.exceptions import NoCredentialsError

app = FastAPI()

# AWS S3 configuration
aws_bucket_name = "test-cloud-storage-bucket"

s3 = boto3.client("s3")

# Function to upload a file to S3
def upload_file_to_s3(file, bucket_name, object_name):
    try:
        s3.upload_fileobj(file, bucket_name, object_name)
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not available")

# Function to list files in S3 bucket
def list_files_in_s3(bucket_name):
    try:
        response = s3.list_objects(Bucket=bucket_name)
        files = [obj["Key"] for obj in response.get("Contents", [])]
        return files
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not available")

# Function to download a file from S3
def download_file_from_s3(bucket_name, object_name):
    try:
        response = s3.get_object(Bucket=bucket_name, Key=object_name)
        return StreamingResponse(content=response["Body"].iter_lines(), media_type="application/octet-stream")
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not available")


# Upload a file to S3
@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    upload_file_to_s3(file.file, aws_bucket_name, file.filename)
    return {"message": "File uploaded successfully"}


# List files in S3
@app.get("/listfiles/")
async def list_files():
    files = list_files_in_s3(aws_bucket_name)
    return {"files": files}


# Download a file from S3
@app.get("/downloadfile/{file_path:path}")
async def download_file(file_path: str):
    return download_file_from_s3(aws_bucket_name, file_path)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
