from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.amazon.aws.operators.emr import EmrCreateJobFlowOperator, EmrAddStepsOperator, EmrTerminateJobFlowOperator
from airflow.providers.amazon.aws.sensors.emr import EmrStepSensor
from airflow.models import Variable

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

# Define the EMR cluster configuration
JOB_FLOW_OVERRIDES = {
    'Name': 'emr-test',
    'ReleaseLabel': 'emr-7.1.0',
    'Instances': {
        'InstanceFleets': [
            {
                'Name': 'MyMasterFleet',
                'InstanceFleetType': 'MASTER',
                'TargetOnDemandCapacity': 1,
                'InstanceTypeConfigs': [{'InstanceType': 'm5.xlarge'}],
            },
            {
                'Name': 'MyCoreFleet',
                'InstanceFleetType': 'CORE',
                'TargetOnDemandCapacity': 1,
                'InstanceTypeConfigs': [{'InstanceType': 'm5.xlarge'}],
            },
        ],
        'KeepJobFlowAliveWhenNoSteps': True,
    },
    'Applications': [
        {'Name': 'Hive'},
        {'Name': 'Hadoop'},
        {'Name': 'Spark'},
    ],
    'VisibleToAllUsers': True,
    'JobFlowRole': 'AmazonEMR-InstanceProfile-20240513T174735',
    'ServiceRole': 'arn:aws:iam::303069582741:role/EMR_fullaccess',
    'LogUri': 's3://emrtest-concat/logs/',
}

# Define the PySpark step configuration
SPARK_STEP = [
    {
        'Name': 'RunPySparkScript',
        'ActionOnFailure': 'CONTINUE',
        'HadoopJarStep': {
            'Jar': 'command-runner.jar',
            'Args': [
                'spark-submit',
                '--deploy-mode', 'cluster',
                '--conf', 'spark.executor.memory=4g',
                's3://emrtest-concat/scripts/concat.py'
            ],
        },
    }
]

# Define the Airflow DAG
with DAG(
    dag_id='emr_cluster_dag',
    default_args=default_args,
    description='A simple EMR DAG to create a cluster, run a PySpark script, and terminate the cluster',
    schedule_interval=None,
    start_date=days_ago(1),
    tags=['example'],
) as dag:

    # Task to create an EMR cluster
    create_emr_cluster = EmrCreateJobFlowOperator(
        task_id='create_emr_cluster',
        job_flow_overrides=JOB_FLOW_OVERRIDES,
    )

    # Task to add a step to the EMR cluster
    step_adder = EmrAddStepsOperator(
        task_id='add_emr_step',
        job_flow_id="{{ task_instance.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
        steps=SPARK_STEP,
    )

    # Sensor to wait for the PySpark step to complete
    step_checker = EmrStepSensor(
        task_id='watch_step',
        job_flow_id="{{ task_instance.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
        step_id="{{ task_instance.xcom_pull(task_ids='add_emr_step', key='return_value')[0] }}",
    )

    # Task to terminate the EMR cluster
    terminate_emr_cluster = EmrTerminateJobFlowOperator(
        task_id='terminate_emr_cluster',
        job_flow_id="{{ task_instance.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
    )

    # Define task dependencies
    create_emr_cluster >> step_adder >> step_checker >> terminate_emr_cluster
