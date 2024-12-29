
# README

This README provides a step-by-step guide to deploying Apache Airflow on AWS using Amazon Managed Workflows for Apache Airflow (MWAA). This guide is designed for users of all experience levels, including freshers.

## Prerequisites

- AWS Account
- IAM Role with necessary permissions
- S3 Bucket for Airflow DAGs and plugins
- AWS CLI installed (optional, but useful for automation)

## Step 1: Set Up an S3 Bucket for Airflow

1. **Log in to the AWS Management Console**.
2. **Navigate to the S3 Service**:
   - In the search bar, type "S3" and select "S3" from the results.

3. **Create an S3 Bucket**:
   - Click the "Create bucket" button.
   - Enter a unique name for your bucket (e.g., `airflow-dags-bucket`).
   - Choose the region where you want to create the bucket.
   - Click "Create bucket" at the bottom of the page.

4. **Create Folders in the S3 Bucket**:
   - Click on your newly created bucket to open it.
   - Click the "Create folder" button.
   - Name the folder `dags` for storing your Airflow DAGs and click "Create folder".
   - Optionally, create folders for `plugins` and `requirements` if you need custom plugins or Python dependencies.

## Step 2: Create an IAM Role for Airflow

1. **Navigate to the IAM Service**:
   - In the search bar, type "IAM" and select "IAM" from the results.

2. **Create an IAM Role**:
   - Click the "Roles" tab on the left, then click "Create role".
   - Choose the "MWAA" service and click "Next: Permissions".
   
3. **Attach Necessary Policies**:
   - Attach the required policies, such as:
     - `AmazonS3ReadOnlyAccess`
     - `AmazonMWAAFullAccess`
     - Any additional policies for accessing specific AWS services like RDS, Redshift, or EMR.

4. **Create the Role**:
   - Name your role (e.g., `MWAA-Airflow-Role`) and click "Create role".

## Step 3: Set Up an Amazon Managed Workflows for Apache Airflow (MWAA) Environment

1. **Navigate to the MWAA Service**:
   - In the search bar, type "MWAA" and select "Amazon Managed Workflows for Apache Airflow" from the results.

2. **Create an MWAA Environment**:
   - Click the "Create environment" button.

3. **Configure the Environment**:
   - **Name**: Provide a name for your Airflow environment (e.g., `my-airflow-env`).
   - **Airflow Version**: Select the version of Airflow you want to use (e.g., 2.x).
   - **S3 Bucket**: Provide the name of the S3 bucket you created (e.g., `airflow-dags-bucket`).
     - Set the `dags` folder path for your DAGs (e.g., `s3://airflow-dags-bucket/dags/`).
     - Optionally set the paths for `plugins` and `requirements`.

4. **Configure Networking**:
   - Select your VPC, subnets, and security groups.
   - Choose the execution role (IAM Role) you created in Step 2.

5. **Set Up Logging**:
   - Enable logging for tasks, workers, schedulers, and web servers.
   - Store logs in CloudWatch for monitoring and debugging.

6. **Create the Environment**:
   - Review the configuration and click "Create environment".

**Note**: It may take some time (15-30 minutes) for the environment to be fully set up.

## Step 4: Upload Airflow DAGs to S3

1. **Prepare Your DAGs**:
   - Create a Python file for your DAG, for example, `example_dag.py`:
     """
     from airflow import DAG
     from airflow.operators.dummy import DummyOperator
     from datetime import datetime

     default_args = {
         'start_date': datetime(2023, 1, 1),
         'retries': 1,
     }

     with DAG(dag_id='example_dag',
              default_args=default_args,
              schedule_interval='@daily') as dag:

         start = DummyOperator(task_id='start')
         end = DummyOperator(task_id='end')

         start >> end
     """

2. **Upload DAG to S3**:
   - Navigate to your S3 bucket in the AWS Management Console.
   - Upload the `example_dag.py` to the `dags` folder of your S3 bucket (e.g., `s3://airflow-dags-bucket/dags/example_dag.py`).

## Step 5: Access the Airflow UI

1. **Navigate to the MWAA Console**:
   - In the MWAA service, click on your newly created environment.

2. **Access the Airflow UI**:
   - In the environment details page, click "Open Airflow UI" to open the Airflow Web UI.

3. **Monitor DAGs**:
   - Once inside the Airflow Web UI, you should see your `example_dag` listed.
   - You can trigger the DAG manually or wait for it to run based on its schedule (`@daily` in this case).

## Step 6: Monitoring and Managing Airflow

1. **Monitor Logs**:
   - View task and execution logs via CloudWatch, where logs are automatically stored if enabled during environment creation.
   - In the Airflow UI, you can also view logs for each task directly.

2. **View Metrics**:
   - Use AWS CloudWatch to monitor system metrics (CPU, memory) and Airflow logs.

## Step 7: (Optional) Using Plugins and Python Dependencies

1. **Add Custom Plugins**:
   - If you have custom Airflow plugins, upload them to the `plugins/` folder in your S3 bucket.
   - The `plugins` folder path should have been specified during environment setup.

2. **Install Python Packages**:
   - Create a `requirements.txt` file with any Python dependencies (e.g., `requests`, `pandas`).
   - Upload the `requirements.txt` file to the `requirements/` folder in your S3 bucket.
   - MWAA will install the packages automatically when the environment is created or updated.

## Conclusion

By following these steps, you have successfully set up an Apache Airflow environment on AWS using Amazon Managed Workflows for Apache Airflow (MWAA). You can now upload and schedule DAGs, monitor execution through the Airflow Web UI, and manage your workflows using the power of AWS services.
