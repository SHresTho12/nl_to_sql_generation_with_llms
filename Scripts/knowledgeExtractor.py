import json
import os
import subprocess
import math
from math import ceil
import requests
import re
# Function to read JSON data from a file
def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Function to write JSON data to a file
def write_json_file(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


def read_schema(file_path):
    """Read the schema file and return its contents."""
    with open(file_path, 'r') as f:
        schema = f.read()
    return schema

def create_prompt(entry, schema):
    """Create a query generation prompt using the database schema and the question."""
    db_id = entry['db_id']
    question = entry['question']

    prompt = (
        f"Database Schema:\n{schema}\n\n"
        f"Question:\n{question}\n\n"
        "Instruction: As an experienced and professional database administrator, your task is to:\n"
        "1. Generate a JSON object with concise knowledge useful for SQL query generation using the Schema and Question.\n"
        "2. Discard any table schema that is not related to the user question and evidence.\n"
        "3. If the question needs join and has nested nature add a label: nested, if not add label: simple.\n"
        "4. If the question has multiple steps list down the steps in steps field,For example: 1. Find the manager who lives in USA 2. Find the Workers under them. Dont generate the query just the descriptive steps, if not just add the single step.\n"
        "5. If the question is asking for some information add possible derivation. For example: if the query asks for monthly salary but the table has a column for yearly salary, the process should be yearly_salary / 12. Add this type of information.\n\n"
        "The JSON object should have fields: question, knowledge, label, steps(list steps to get the result query). Just generate the JSON object.Dont include any sql query. No explanation is needed. Send the response in code block\n\n"
        "Knowledge:"
    )
    return prompt

def reduce_inserts(schema):
    """Reduce INSERT statements in the schema to a maximum of 2 per table."""
    create_table_pattern = re.compile(r'(CREATE TABLE.*?;)', re.S)
    insert_pattern = re.compile(r'(INSERT INTO.*?;)', re.S)
    
    tables = create_table_pattern.split(schema)
    new_schema = ""
    
    for i in range(len(tables)):
        if 'CREATE TABLE' in tables[i]:
            new_schema += tables[i]
            # Find all inserts after the current table declaration
            inserts = insert_pattern.findall(tables[i+1])
            limited_inserts = inserts[:2]  # Limit to 2 insert statements
            new_schema += '\n'.join(limited_inserts).strip() + '\n'
            # Remove the handled inserts from the next segment
            tables[i+1] = insert_pattern.sub('', tables[i+1], count=len(inserts)).strip()
        else:
            new_schema += tables[i].strip() + '\n'
    
    # Remove any multiple consecutive newlines
    new_schema = re.sub(r'\n+', '\n', new_schema)
    
    return new_schema

def testSchema(spider_data, schema_base_path):
    entry = spider_data[40]
    db_id = entry['db_id']
    schema_file_path = f'{schema_base_path}/{db_id}/schema.sql'
    schema = read_schema(schema_file_path)
    print(len(schema))
    print(schema)
    processed_schema = reduce_inserts(schema)
    print(len(processed_schema))
    print(processed_schema)



def process_knowledge_extraction(spider_data, schema_base_path, output_file, batch_size=10):
    """Process entries in spider_data in batches, generate SQL queries, and save incrementally."""
    updated_data = []
    total_entries = len(spider_data)
    total_batches = ceil(total_entries / batch_size)
    id = 0
    for batch_idx in range(total_batches):
        batch_start = batch_idx * batch_size
        batch_end = min(batch_start + batch_size, total_entries)
        batch = spider_data[batch_start:batch_end]

        if batch_idx>2:
            print(batch_idx)
            break;
        for idx, entry in enumerate(batch, start=batch_start + 1):
            db_id = entry['db_id']
            schema_file_path = f'{schema_base_path}/{db_id}/schema.sql'
            schema = read_schema(schema_file_path)
            processed_schema = reduce_inserts(schema)
            prompt = create_prompt(entry, processed_schema)
            
            # print(f"Generated SQL for entry {idx}: {prompt}")
            url = 'http://127.0.0.1:8000/query/LISP_TRANSLATOR'
            headers = {
                'accept': 'application/json',
                'Content-Type': 'text/plain',
            }
            response = requests.post(url, headers=headers, data=prompt)
            print(response.json())
            # Parse the response JSON
            response_data = response.json()
            value_str = response_data['data']['value']

            # Step 4: Convert the value to a JSON object
            value_json = json.loads(value_str)

            # Add an ID to the JSON object (you can generate or use an existing one)
            value_json['db_id'] = db_id
            value_json['question'] = entry['question']
            value_json['id'] = id
            id += 1
                        
            print(f"Processed entry {idx}/{total_entries}")
            print(value_json)
            # Add the  generated SQL to the entry
            # entry['generated_sql'] = generated_sql
            updated_data.append(value_json)
        # Save the updated data incrementally
        with open(output_file, 'w') as f:
            json.dump(updated_data, f, indent=4)

        print(f"Processed batch {batch_idx + 1}/{total_batches}")


# Step 1: Read data from dev.json
dev_file_path = './test_data/dev.json'
dev_data = read_json_file(dev_file_path)

# Step 2: Import schema information based on db_id
# Process the data and save the results
schema_file_path = f'./test_database'
output_file = './spider_data_with_knowledge1.json'


# testSchema(dev_data, schema_file_path)

process_knowledge_extraction(dev_data, schema_file_path, output_file)
# # Step 3: Create a cURL request and send it
# curl_command = f"curl -X POST -H 'Content-Type: application/json' -d '{json.dumps(dev_data)}' http://example.com/api"

# # Execute the cURL command and get the response
# result = subprocess.run(curl_command, shell=True, capture_output=True, text=True)

# # Step 4: Save the response in a new JSON file
# response_data = json.loads(result.stdout)
# output_file_path = 'response.json'
# write_json_file(response_data, output_file_path)

# print(f'Response saved to {output_file_path}')
