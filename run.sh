#!/bin/bash

source ~/anaconda3/etc/profile.d/conda.sh
conda activate vis

streamlit run vis.py --server.maxMessageSize 1000 --runner.magicEnabled false