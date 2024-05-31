import os
import json

def merge_json_files(input_files, output_file):
    merged_data = []

    try:
        # Get the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Read and merge each JSON file
        for file in input_files:
            file_path = os.path.join(current_dir, file)
            with open(file_path, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    merged_data.extend(data)
                else:
                    raise ValueError(f"JSON file {file} does not contain a list of JSON objects.")
    except Exception as e:
        print(f"Error occurred while processing file {file}: {str(e)}")
        return

    # Write the merged data to a new JSON file
    try:
        with open(output_file, 'w') as outfile:
            json.dump(merged_data, outfile, indent=4)
        print(f"Merged data successfully written to {output_file}")
    except Exception as e:
        print(f"Error occurred while writing merged data to {output_file}: {str(e)}")

# Specify the input and output files
input_files = [
    'batch1.json',
    'batch2.json',
    'batch3.json',
    'batch4.json',
    'batch5.json'
]
output_file = 'spider_data_wk_gpt.json'

# Merge the JSON files
merge_json_files(input_files, output_file)
