# AWS-Overlord

# Project Overview

This project implements an automated job processing system utilizing AWS Lambda, AWS Batch, MongoDB, and AWS API Gateway. It is designed to handle job submissions to AWS Batch upon receiving external requests, manage and track these submissions, and record the outcomes in a structured way.

## Components

- **AWS API Gateway**: Acts as the entry point for external job submission requests.
- **Lambda Function 1**: Responsible for generating a unique job ID based on input data, submitting the job to AWS Batch, and logging the submission details in MongoDB.
- **Lambda Function 2**: Activated upon the completion of an AWS Batch job, it handles logging of the job results in MongoDB.
- **MongoDB Database**: Organized into three collections - `jobs_collection`, `runs_collection`, and `logs_collection` - for effective management and logging of job data.

## Prerequisites

- An AWS account.
- A MongoDB Atlas account.
- Python 3.x installed locally (needed for AWS Lambda functions).
- Docker installed locally (used for testing AWS Batch jobs).
- AWS CLI configured on your local machine.

## Setup Instructions

### MongoDB Atlas Setup

1. Create a cluster in MongoDB Atlas.
2. Setup a database named `<db_name>` with three collections: `jobs`, `runs`, `logs`.
3. Adjust network access settings to allow connections from AWS services. Consider using AWS PrivateLink for enhanced security.

### AWS Setup

#### IAM Role Creation

- Create an IAM role for Lambda functions with permissions for AWS Batch, CloudWatch Logs, and AWS API Gateway execution.
- Create an IAM role for AWS Batch that allows it to execute jobs and log to CloudWatch.

#### AWS API Gateway

- Create a new REST or HTTP API.
- Define a new resource and method (e.g., POST) to trigger Lambda Function 1.
- Deploy the API.

#### Lambda Functions

- **SubmitBatchJob**: Set up with the Python 3.x runtime, using the IAM role with the necessary permissions. It generates a unique job ID, submits the job to AWS Batch, and logs the details to MongoDB when triggered by the AWS API Gateway.
  
- **Lambda Function 2**: Triggered by CloudWatch Events upon AWS Batch job completion, it logs the job results into MongoDB.

#### AWS Batch Configuration

- Create a Compute Environment.
- Set up a Job Queue linked to the Compute Environment.
- Define a Job Definition specifying the Docker image for job processing.

### Environment Variables

Configure the following environment variables in Lambda functions for MongoDB connectivity:

- `MONGODB_URI`: MongoDB connection string.
- `DB_NAME`: The name of the database in MongoDB.

## Usage

### Submitting a Job

- Send a POST request to the AWS API Gateway endpoint with the required data payload to trigger Lambda Function 1. This function generates a unique ID for the job, submits it to AWS Batch, and logs the submission in `jobs_collection`.

### Monitoring and Logs

- **AWS Batch Console**: Use this to monitor job statuses.
- **MongoDB Collections**:
  - `jobs_collection`: View details of submitted jobs.
  - `runs_collection`: Track processed jobs.
  - `logs_collection`: Access logs for job outcomes.

## Security Considerations

- Use AWS Secrets Manager to secure MongoDB credentials.
- Implement VPC Peering or AWS PrivateLink for secure communication between AWS services and MongoDB Atlas.
- Apply the principle of least privilege when setting up AWS IAM roles and policies.

## Troubleshooting

- **Job Submission Failures**: Check Lambda execution role permissions, AWS Batch configurations, and API Gateway integration.
- **MongoDB Connectivity**: Verify MongoDB network access settings and Lambda function environment variables.
