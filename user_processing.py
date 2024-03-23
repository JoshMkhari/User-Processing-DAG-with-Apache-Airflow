from datetime import datetime
import json
from pandas import json_normalize

from airflow import DAG

from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.http.sensors.http import HttpSensor

default_args = {
    'start_date': datetime(2020, 1, 1)
}

def _processing_user(ti):
    users = ti.xcom_pull(task_ids=['extracting_user'])
    if not len(users) or 'results' not in users[0]:
        raise ValueError('User is empty')
    user = users[0]['results'][0]
    processed_user = json_normalize({
        'firstname': user['name']['first'],
        'lastname': user['name']['last'],
        'country': user['location']['country'],
        'username': user['login']['username'],
        'password': user['login']['password'],
        'email': user['email']
    })
    processed_user.to_csv('/tmp/processed_user.csv', index=None, header=False)
    
def _store_user():
    hook = PostgresHook(postgres_conn_id='postgres')
    with hook.get_conn() as connection:

        hook.copy_expert(
            sql="COPY users FROM stdin WITH DELIMITER as ','",
            filename='/tmp/processed_user.csv'
        )
        connection.commit()

with DAG('user_processing', schedule_interval='@daily',
        default_args=default_args,
        catchup=False) as dag:
        # Define tasks/operators
        
    creating_table = PostgresOperator(
        task_id='creating_table',
        postgres_conn_id='postgres',
        sql='''
            CREATE TABLE IF NOT EXISTS users (
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                country TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                email TEXT NOT NULL PRIMARY KEY
            );
        ''' 
    )
    
    
    is_api_available = HttpSensor(
        task_id='is_api_available',
        http_conn_id='user_api',
        endpoint='api/'
    )
    
    extracting_user = SimpleHttpOperator(
        task_id='extracting_user',
        http_conn_id='user_api',
        endpoint='api/',
        method='GET',
        response_filter=lambda response: json.loads(response.text),
        log_response=True
    )
    
    processing_user = PythonOperator(
        task_id='processing_user',
        python_callable=_processing_user
    )
    
    store_user = PythonOperator(
        task_id='store_user',
        python_callable=_store_user
    )
    
    
creating_table >> is_api_available >> extracting_user >> processing_user >> store_user
