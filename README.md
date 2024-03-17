Updated upstream
G-T2KG
We are still working on the documentation and commenting the code. The final result will be available soon. Thank you for your patience.
=======
# Integrating OpenIE Syntactic Cleaning and LLMs Validation for Domain-Independent Knowledge Graph Construction
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
>>>>>>> Stashed changes
