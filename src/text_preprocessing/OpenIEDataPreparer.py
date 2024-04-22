import nltk
import json
from tqdm import tqdm
import argparse
## read data
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

class OpenIEDataPreparer:
    ## data path: after coreferences resolution (json file)
    def __init__(self, data_path, output_path, corpus):
        self.data_path = data_path
        self.output_path = output_path
        self.data = {}
        self.result = []
        self.sentences = []
        self.corpus = corpus
        
        ## paragraph -> sentences
    def split_paragraph(self,paragraphe):
        sentences = nltk.sent_tokenize(paragraphe)
        return sentences
        
    
    ## computer sc 
    def prepare_setences(self):
        data = read_json_file(self.data_path)
        print(len(self.corpus))
        if str(self.corpus) == "computer_science": 
            abstracts = [paragraph["abstract"] for paragraph in data.values()]
    #         with open(output_path, 'w', encoding='utf-8') as output_file:
            for abstract in abstracts:
                sentences = self.split_paragraph(abstract)
                for sentence in tqdm(sentences, desc="Processing Sentences", unit="sentence", leave=False):
    #                     output_file.write(sentence.strip() +'\n')
                    self.sentences.append(sentence.strip())
        elif self.corpus == "Music":
            paragraphs = [paragraph["paragraph"] for paragraph in data.values()]
            for paragraph in paragraphs:
                sentences = self.split_paragraph(paragraph)
                for sentence in tqdm(sentences, desc="Processing Sentences", unit="sentence", leave=False):
    #               output_file.write(sentence.strip() +'\n')
                    self.sentences.append(sentence.strip())

        else:
            print("invalid corpus name!")
            return

    def is_valid_sentence(self, sentence):
        return not sentence.startswith(('(C)', '(c)')) \
               and len(sentence) >= 20 \
               and not sentence.startswith(':') \
               and any(c.isalpha() for c in sentence) \
               and not sentence.startswith('Copyright')
    
    def clean_sentences(self):
    # Apply the filter and strip each sentence
        filtered_sentences = [sentence.strip() for sentence in self.sentences if self.is_valid_sentence(sentence)]
        self.result = filtered_sentences
#         Open the output file in write mode and write the filtered lines
        with open(self.output_path, "w",encoding='utf-8' ) as file:
            file.write('\n'.join(filtered_sentences))
    
    def run(self):
        self.prepare_setences()
        self.clean_sentences()

if __name__ == "__main__":
    print("\n Segmentation...")
    parser = argparse.ArgumentParser(description="Cleaning and segmentation")
    parser.add_argument("corpus", type=str, help="Corpus type (e.g., Music or Computer_science)")
    parser.add_argument("input_file", type=str, help="name of the input file inside the data G-T2KG_input directory")
    args = parser.parse_args()
    input_path = "../outputs/"+args.input_file+"_coref.json"
    output_path = "../outputs/"+args.input_file+"_oie.txt"
    odp = OpenIEDataPreparer(input_path, output_path, args.corpus)
    odp.run()
