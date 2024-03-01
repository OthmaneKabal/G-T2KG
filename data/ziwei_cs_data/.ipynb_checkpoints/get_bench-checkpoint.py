import json
import sys

def filter_json_by_ids(json_file_path, output_file_path, id_list):
    with open(json_file_path, 'r') as json_file:
        json_data = json.load(json_file)
    
    filtered_json = {}
    for paper_id, paper_data in json_data.items():
        if paper_data['_id'] in id_list:
            filtered_json[paper_id] = paper_data
    
    with open(output_file_path, 'w') as output_file:
        json.dump(filtered_json, output_file, indent=4)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python filter_json.py <input_json_file> <output_file> <id1> [<id2> <id3> ...]")
        sys.exit(1)

    input_json_file = sys.argv[1]
    output_file = sys.argv[2]
    id_list = sys.argv[3:]

    filter_json_by_ids(input_json_file, output_file, id_list)
    print(f"Filtered JSON saved to {output_file}")