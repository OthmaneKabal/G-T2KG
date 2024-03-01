import json

## read data -----> utilities
def read_json_file(file_path):
    """
    Read a JSON file and return its contents as a Python dictionary.

    :param file_path: The path to the JSON file.
    :type file_path: str
    :return: A dictionary representing the JSON data.
    :rtype: dict
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in file {file_path}: {e}")
    except Exception as e:
        print(f"An error occurred while reading the file {file_path}: {e}")


def save_to_json(path,data):
        with open(path, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, ensure_ascii=False, indent=2)