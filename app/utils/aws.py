import boto3
from flask import current_app
import uuid

def upload_file_to_s3(file, acl="public-read"):
    """
    Uploads a file to S3 and returns the URL
    """
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
            region_name=current_app.config['AWS_DEFAULT_REGION']
        )
        
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        new_filename = f"{str(uuid.uuid4())}.{file_extension}"
        
        # Upload file
        s3_client.upload_fileobj(
            file,
            current_app.config['S3_BUCKET'],
            new_filename,
            ExtraArgs={
                'ACL': acl,
                'ContentType': file.content_type
            }
        )
        
        # Generate URL
        url = f"https://{current_app.config['S3_BUCKET']}.s3.amazonaws.com/{new_filename}"
        return url
        
    except Exception as e:
        print(f"Error uploading file to S3: {str(e)}")
        return None