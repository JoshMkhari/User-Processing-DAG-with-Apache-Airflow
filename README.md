# User Processing DAG with Apache Airflow
This repository contains a DAG (Directed Acyclic Graph) built with Apache Airflow that processes user data from an API and stores it in a Postgres database.

## What the DAG Does:

### Checks API Availability: 
The DAG first uses an HttpSensor to confirm the user API is available before proceeding.
Extracts User Data: If the API is available, a SimpleHttpOperator retrieves user data as JSON.
### Processes User Data: 
A PythonOperator parses the retrieved JSON and transforms it into a normalized format.
Stores User Data: Another PythonOperator utilizes a PostgresHook to connect to the database and store the processed user data in a table.

## Key Learnings:

### Operators:
#### HttpSensor: 
This sensor waits for a specific endpoint to return a successful response before continuing the DAG execution.
#### SimpleHttpOperator: 
This operator makes an HTTP request to a specified endpoint and retrieves the response.
#### PythonOperator: 
This operator allows you to execute custom Python functions within the DAG.
#### XCom: 
The DAG demonstrates how to utilize XCom to share data between tasks. The processing_user task retrieves user data extracted by the extracting_user task using XCom pull.
#### Hooks: 
The DAG utilizes a PostgresHook to interact with the Postgres database for user data storage.

## Future Learnings:

### Quest Operator
### Advanced Data Sharing: 
While XCom is used here, exploring options like message queues or plugins for larger-scale data exchange would be beneficial.
