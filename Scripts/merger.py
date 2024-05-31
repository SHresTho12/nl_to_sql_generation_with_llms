import json

def merge_json_files(input_files, output_file):
    merged_data = []

    # Read and merge each JSON file
    for file in input_files:
        with open(file, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                merged_data.extend(data)
            else:
                raise ValueError(f"JSON file {file} does not contain a list of JSON objects.")

    # Write the merged data to a new JSON file
    with open(output_file, 'w') as outfile:
        json.dump(merged_data, outfile, indent=4)

# Specify the input and output files
input_files = [
    'spider_data_with_knowledge1.json',
    'spider_data_with_knowledge2.json',
    'spider_data_with_knowledge3.json',
    'spider_data_with_knowledge4.json',
    'spider_data_with_knowledge5.json',
    'spider_data_with_knowledge6.json',
    'spider_data_with_knowledge7.json',
    'spider_data_with_knowledge8.json',
    'spider_data_with_knowledge9.json',
    'spider_data_with_knowledge10.json',
    'spider_data_with_knowledge11.json',
    'spider_data_with_knowledge12.json',
    'spider_data_with_knowledge13.json'
]
output_file = 'spider_data_with_knowledge.json'

# Merge the JSON files
merge_json_files(input_files, output_file)
