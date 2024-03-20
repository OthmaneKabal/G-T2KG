
# Integrating OpenIE Syntactic Cleaning and LLMs Validation for Domain-Independent Knowledge Graph Construction (G-T2KG)
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
./Preprocessing.sh Arg
```
 
Replace Arg with either **Music** or **computer_science**.

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
### Hyponymy Extraction
Navigate to the following directory: `/src/informations_extraction`.
execute the following script
```bash
hyponyms_extractor.py
```
## Post-traitment:

### Syntactic cleaning
Navigate to the following directory: `/src/post_processing/syntactic_cleaning`
* execute the following script
```bash
TriplesPostProcessing.py
```
### Mapping
Navigate to the following directory: `/src/post_processing/mapping`
* execute the following script
```bash
mapping.py
```
## Triplets Validator
Navigate to the following directory: `/src/triplets_validator`.
execute the following script 
```bash
Triplets_Validator.py
```
# Contacts
If you have any questions about our work or issues with the repository, please contact Othmane KABAL by email othmane.kabal@univ-nantes.fr