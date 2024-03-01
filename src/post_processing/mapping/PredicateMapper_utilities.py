import json
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import pandas as pd


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
        
def loadVerbMap(verb_map_path):
    verb_info = pd.read_csv(verb_map_path, sep=',')
    verb_map = {}
    for i,r in verb_info.iterrows():
        for j in range(34):
            verb = r['v' + str(j)]
            if str(verb) != 'nan':
                verb_map[verb] = r['predicate']
    return verb_map

def encode_and_store(sentences, model, file_path):
    # Encode sentences
    embeddings = model.encode(sentences, convert_to_tensor=True)

    # Create a dictionary with sentences as keys and their embeddings as values
    embeddings_dict = {sentence: embedding.tolist() for sentence, embedding in zip(sentences, embeddings)}

    # Save the dictionary to a JSON file
    with open(file_path, 'w') as file:
        json.dump(embeddings_dict, file)

def load_embeddings(file_path):
    # Load the embeddings from the JSON file
    with open(file_path, 'r') as file:
        embeddings_dict = json.load(file)

    # Convert the embeddings from list to numpy array
    embeddings_dict = {sentence: [float(value) for value in embedding] for sentence, embedding in embeddings_dict.items()}
    return embeddings_dict




# Example sentences
#sentences = list(verb_map.keys())

# Model initialization
#model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

# File path to store and load embeddings

#embd_path = 'C:/Users/admin-user/Desktop/my_phd/implementations_KG/resources/predicate_embeddings.json'

# Encode sentences, store in a file, and then load them
#encode_and_store(sentences, model, embd_path)
#loaded_embeddings = load_embeddings(file_path)

