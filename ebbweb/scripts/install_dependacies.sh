#!/bin/bash

# Install dependencies for the blockchain code

# Install Python3 and pip
sudo apt update
sudo apt install -y python3 python3-pip

# Install required Python libraries
pip3 install -r requirements.txt

