# Example python script hosted on AWS Lambda #

## What is this? ##

Python script running on AWS Lambda with functions:

- Connect to PostgreSQL database
- Generate CSV files
- Upload the CSV files to AWS S3

Developed in Dec 2024.

## Requirements ##

- AWS account
- AWS Access Key ID (can be obtained at IAM > Users)
- AWS Secret Access Key (can be obtained at IAM > Users)
- Region (e.g. ap-southeast-1)
- Role / ARN (e.g. arn:aws:iam::123456789012:role/lambda-role)
- DB_HOST
- DB_PORT
- DB_NAME
- DB_USER
- DB_PASSWORD
- S3_BUCKET
- S3_KEY_PREFIX (e.g. reports)

## Installation ##

This project utilizes `awscli` to configure AWS, manage function code and function configuration. So, before clone this project, make sure you have `awscli` installed on your machine.

```bash
# Install the AWS CLI
pip install awscli

# Verify the awscli installation
aws --version
```

Then configure the AWS account.

```bash
aws configure
```

Input your details and input `json` as default output format.

### 1) Clone this project ###

You may use this script by clone this project using git command or download as .zip file then extract it.

### 2) Understand the project structure ###

```text
This Project
│
├── package/                    # folder to be uploaded to AWS Lambda
│   ├── boto3
│   ├── lambda_function.py      # python script that we created to run on Lambda
│   ├── psycopg2
│   ├── requirements.txt        # contains dependencies - install it using the command 
│   │                           # "pip install -r requirements.txt -t ."
│   ├── ... (other dependencies)
│
├── event.json                  # used for testing running scripts
└── README.md
```

### 3) Prepare the ZIP file to be uploaded to AWS Lambda ###

After prepare the dependencies and the main script, compress it to .zip file

```bash
# make sure you are in the "package" directory
cd package

# zip all the files
zip -r ../lambda_function.zip .
```

### 4) Create a new function in Lambda ###

For creating a new function in Lambda, we must have `AWS Role/ARN` (for creating Role/ARN, please see "Create AWS New Role/ARN" section below)

```bash
# make sure you are outside the "package" directory, you are in the root directory of this project
cd ..

# create a new Lambda function
aws lambda create-function \
    --function-name GenerateReports \
    --runtime python3.11 \
    --role arn:aws:iam::123456789012:role/lambda-role \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://lambda_function.zip
```

Note:

- `GenerateReports` is function name
- `python3.11` is runtime Python version
- `role` is your AWS role/ARN
- `handler` is your function name
- `zip-file` is your ZIP file

### 5) Set ENV in Lambda ###

```bash
aws lambda update-function-configuration \
    --function-name GenerateReports \
    --environment "Variables={DB_HOST=localhost,DB_PORT=5432,DB_NAME=xxx_db,DB_USER=user,DB_PASSWORD=xxx,S3_BUCKET=bucket-name,S3_KEY_PREFIX=reports}"
```

### 6) Update configuration in Lambda ###

```bash
aws lambda update-function-configuration \
    --function-name GenerateReports \
    --timeout 900
```

### 7) Running test ###

```bash
aws lambda invoke \
    --function-name GenerateReports \
    --payload file://event.json \
    response.json
```

It will generate `response.json`, then you can check the response details.

### 8) Update code (if needed) ###

```bash
aws lambda update-function-code \
    --function-name GenerateReports \
    --zip-file fileb://lambda_function.zip
```

## Dependecies ##

- psycopg2-binary
- boto3

## *IMPORTANT NOTE ##

We need `psycopg2-binary` for connect to PostgreSQL, to install it - please use from [https://github.com/jkehler/awslambda-psycopg2](https://github.com/jkehler/awslambda-psycopg2). Clone it first, then copy the files based on your Python version (in this project we will use Python 3.11) then paste it into the “package” directory.

## Create AWS New Role/ARN ##

1. Login to AWS Management Console
2. Go to IAM service
3. Choose “Roles” on the sidebar menu, then click “Create role”
4. Choose “AWS Service” as trusted entity
5. Choose “Lambda” from service list, then click “Next”
6. For Permissions, add ”AmazonS3FullAccess” so this role can access to S3, then click “Next”
7. Input the role name, like “lambda-s3-role”
8. Click “Create role”
