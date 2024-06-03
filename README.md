# Enhancing Domain-Independent Knowledge Graph Construction through OpenIE Cleaning and LLMs Validation (G-T2KG)
This repository provides the code used to build knowledge graph 
from text (G-T2KG)

NB: To run this code, you must have the OpenIE6 tool code that works well.

# Content of the repository
* /src:  all the source code
* /src/text_preprocessing: The scripts used for data cleaning and their segmentation (sentences) to prepare them for the triplet extraction phase.
* /src/informations_extraction: Contains the scripts for extracting triplets from sentences (using OpenIE 6 and hyponymy patterns).
* /src/post_processing: Contains the scripts for two components: syntactic cleaning for cleaning the triplets obtained by the OpenIE system and the mapping component.
* /src/triplets_validator: Contains the scripts for the triplet validation component (Prompt used in GPT-4).
* /data: Contains the data used.
* /data/Benchmarks: The two Benchmarks used for evaluation (Computer Science and Music)
* /data/corporas: The two corpora used  (Computer Science and Music).
* /resources: Contains the external resources used, specifically the predicate mapping dictionary.
# How to run
## Component 1: Text Preprocessing

Navigate to the following directory: `/src/text_preprocessing`.

Run the `Preprocessing.sh` script with an argument (which specifies the corpus: Music or computer_science) using the following command:

```bash
./Preprocessing.sh Arg file_name
```
 
Replace Arg with either **Music** or **computer_science**.
Replace file_name with your json file that you want to extract KG from (this file should be inside the directory \data\G-T2KG_input )

The output of this component will be saved in `src/outputs`. 
Two files will be generated: one for resolving coreferences and the other for segmenting the corpus into sentences.
## Component 2: Information Extraction
### Triplet Extraction
This subcomponent takes as input the sentences segmented by (Component 1). To do this, you must have OpenIE6 properly functioning. Navigate to the OIE6 directory and execute the following command to extract triplets:

```bash
python run.py --mode predict --inp input_path --out output_path --rescoring --task oie --gpus 0 --oie_model models/oie_model/epoch=14_eval_acc=0.551_v0.ckpt --conj_model models/conj_model/epoch=28_eval_acc=0.854.ckpt --rescore_model models/rescore_model --num_extractions 5
```
* input_path: the set of sentences extracted and saved in  '/src/outputs'
* output_path: /src/outputs/OIE_triplets.txt (path to save extracted triplets)
#### OpenIE Triplets Converter Formats
This script is dedicated to formatting OpenIE 6 output into JSON for easy manipulation in subsequent components.
```bash
TripletExtractionConverter.py file_name
```
the output will be saved `src/outputs/file_name_oie_triplets.json`
### Hyponymy Extraction
Navigate to the following directory: `/src/informations_extraction`.
execute the following script
```bash
hyponymsExtractor.py file_name
```
Replace file_name with your json file that you want to extract KG from (this file should be inside the directory \data\G-T2KG_input )
## Post-traitment:

### Syntactic cleaning
Navigate to the following directory: `/src/post_processing/syntactic_cleaning`
* execute the following script
```bash
python TriplesPostProcessing.py file_name --root_option option
```
Option: The option to use for extracting noun phrase head
- stanza: Use the dependency tree.
- gpt: Use ChatGPT-4. In this case, you should specify the API key to customize the API with `--gpt_key API-key`.
The result will be stored at `src/outputs/file_name_oie_cleaned_triplets.json`
### Merge triplets 

Merge the cleaned triplets and the hyponymy triplets
```bash
python TriplesPostProcessing.py file_name --root_option option
```
The result will be stored at `src/outputs/file_name_All_triplets.json`

## Triplets Validator
Navigate to the following directory: `/src/triplets_validator`.
execute the following script 
```bash
Triplets_Validator.py file_name --gpt_key API-key
```
API key: the api key to customize gpt-4
The result will be stored at `src/outputs/file_name_validated_triplets.json`
## Mapping
Navigate to the following directory: `/src/post_processing/mapping`
* execute the following script
```bash
mapping.py file_name
```
The result will be stored at `src/outputs/file_name_KG.json`

# Contacts
If you have any questions about our work or issues with the repository, please contact Othmane KABAL by email othmane.kabal@univ-nantes.fr
