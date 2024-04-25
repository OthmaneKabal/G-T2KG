import spacy
from spacy.tokens import Doc
import json
import copy
import argparse
from tqdm import tqdm

def read_json_file(file_path):
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

def save_json_file(output_path, json_data):
    with open(output_path, 'w') as json_file:
        json.dump(json_data, json_file, indent=2)
        print("file was saved succesfully")

class CoreferencesResolver:

    def __init__(self, data_path, output_path, corpus):
        self.data_path = data_path
        self.output_path = output_path
        self.data = {}
        self.result_data = {}
        self.corpus = corpus

    def replace_references(self, doc: Doc) -> str:
        token_mention_mapper = {}
        output_string = ""
        clusters = [
            val for key, val in doc.spans.items() if key.startswith("coref_cluster")
        ]

        for cluster in clusters:
            first_mention = cluster[0]
            first_mention_Endposition = first_mention[0].idx + len(first_mention.text)
            for mention_span in list(cluster)[1:]:
                if first_mention_Endposition > mention_span[0].idx:
                        pass
                else:
                    token_mention_mapper[mention_span[0].idx] = first_mention.text + mention_span[0].whitespace_
                    for token in mention_span[1:]:
                        token_mention_mapper[token.idx] = ""

        for token in doc:
            if token.idx in token_mention_mapper:
                output_string += token_mention_mapper[token.idx]
            else:
                output_string += token.text + token.whitespace_
        return output_string

    def coreference_resolver(self, text, coref_spacy):
        doc = coref_spacy(text)
        return self.replace_references(doc)
    
    def corpus_coreferences_resolution(self):
        coref_spacy = spacy.load("en_coreference_web_trf")
        self.data = read_json_file(self.data_path)
        temp_data = copy.deepcopy(self.data)
        if self.corpus == "computer_science":
            for element in tqdm(self.data, desc="Processing abstracts"):
               temp_data[element]["abstract"] = self.coreference_resolver(self.data[element]["abstract"], coref_spacy)
        elif self.corpus == "Music":
            for element in tqdm(self.data, desc="Processing abstracts"):
                temp_data[element]["paragraph"] = self.coreference_resolver(self.data[element]["paragraph"], coref_spacy)
        else:
            print("corpus name invalid!")
            return
        self.result_data = temp_data
        save_json_file(self.output_path, self.result_data)

if __name__ == "__main__":
    print("coreference Resolution ...")
    parser = argparse.ArgumentParser(description="Coreferences Resolution in Text Corpora")
    parser.add_argument("corpus", type=str, help="Corpus type (e.g., Music or Computer_science)")
    parser.add_argument("input_file", type=str, help="name of the input file inside the data G-T2KG_input directory")
    args = parser.parse_args()
    if args.corpus == "Music":
        data_path = "../../data/G-T2KG_input/"+args.input_file+".json"
    elif args.corpus == "computer_science":
        data_path = "../../data/G-T2KG_input/"+args.input_file+".json"
    else:
        print("invalid argument !")
    output_path = "../outputs/"+args.input_file+"_coref.json"
    cr = CoreferencesResolver(data_path, output_path, args.corpus)
    cr.corpus_coreferences_resolution()

