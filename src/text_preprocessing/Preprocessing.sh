#!/bin/bash

# Check if conda environment exists
conda activate coref-env 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Environment 'coref-env' does not exist. Creating..."
    conda create -n coref-env python=3.9 -y
else
    echo "Environment 'coref-env' already exists."
fi

# Activate the environment
conda activate coref-env

# Install packages
pip install spacy-experimental==0.6.2
pip install https://github.com/explosion/spacy-experimental/releases/download/v0.6.1/en_coreference_web_trf-3.4.0a2-py3-none-any.whl
pip install nltk

# Execute Python scripts with arguments
python CoreferencesResolver.py "$1" "$2"
python OpenIEDataPreparer.py "$1" "$2"

