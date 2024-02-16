import json
import hashlib
import uuid
import pymongo
import os
import boto3

# Setup MongoDB client
client = pymongo.MongoClient(os.environ['MONGODB_URI'])
db = client[os.environ['DB_NAME']]
jobs_collection = db['jobs']

# Initialize the boto3 client for AWS Batch
batch_client = boto3.client('batch')


def sha256_to_guid(data):
    hash_object = hashlib.sha256(data.encode())
    first_16_bytes = hash_object.digest()[:16]
    return str(uuid.UUID(bytes=first_16_bytes))


def get_keyVals(j, key_str=""):
    if isinstance(j, dict):
        keys = sorted(j.keys())
        for key in keys:
            for x in get_keyVals(j[key], key_str + ":" + key if key_str else key):
                yield x
    elif isinstance(j, list):
        for i, v in enumerate(sorted(j)):
            for x in get_keyVals(v, f"{key_str}[{i}]"):
                yield x
    else:
        yield f"{key_str}: {str(j).strip()}"


def submit_batch_job(user_data, correlation_id):
    
    program = user_data.get('program')
    env_variables = user_data['user_data']['DATA']
    
   


    job_definitions = {
        'program1': 'job-definition-name-for-program1',
        'program2': 'job-definition-name-for-program2',
        'test-batch': 'test-batch'
    }
    job_definition = job_definitions.get(program)
    print(f"Program: {program}")
    print(f"Job Definition: {job_definition}")
    print(f"env_variables: {env_variables}")
    


    if not job_definition:
        raise ValueError(f"Unsupported program: {program}")

    environment_overrides = [{'name': k, 'value': str(v)} for k, v in env_variables.items()]
    
    print(environment_overrides)

    response = batch_client.submit_job(
        jobName=f"{program}-{correlation_id}",
        jobQueue='default-queue',
        jobDefinition=job_definition,
        containerOverrides={'environment': environment_overrides}
    )
    return response


def submit_job(data):
    correlation_id = sha256_to_guid(json.dumps(data))
    existing_job = jobs_collection.find_one({'correlationID': correlation_id})
    if existing_job:
        return {"statusCode": 409,
                "body": json.dumps({"message": "Job already submitted", "correlationID": correlation_id})}

    try:
        batch_response = submit_batch_job(data, correlation_id)
        job_status = "submitted"
        response_message = "Job submitted successfully"
        aws_batch_job_id = batch_response.get("jobId")
    except Exception as e:
        job_status = "failed to submit"
        response_message = f"Failed to submit job: {str(e)}"
        aws_batch_job_id = None

        # Log detailed error information in MongoDB
        jobs_collection.insert_one({
            "correlationID": correlation_id,
            "status": job_status,
            "error": str(e),
            "AWSBatchJobId": aws_batch_job_id
        })

        return {
            "statusCode": 500,
            "body": json.dumps({"message": response_message, "correlationID": correlation_id, "status": job_status})
        }

    # Log successful job submission in MongoDB
    jobs_collection.insert_one({
        "correlationID": correlation_id,
        "status": job_status,
        "AWSBatchJobId": aws_batch_job_id
    })

    return {
        "statusCode": 200,
        "body": json.dumps({"message": response_message, "correlationID": correlation_id, "status": job_status})
    }


def lambda_handler(event, context):
    
    data = json.loads(event['body']) if 'body' in event else event
    response = submit_job(data)
    return {
        'statusCode': response['statusCode'],
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': response['body']
    }
