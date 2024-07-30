#!/bin/bash

ollama serve &
sleep 10
python3 main.py
