#!/usr/bin/env bash

pip3 install -U setuptools wheel pip
pip3 install notebook
pip3 install -r requirements.txt
jupyter labextension install @jupyter-widgets/jupyterlab-manager
