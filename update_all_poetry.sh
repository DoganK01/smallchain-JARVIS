#!/bin/bash

# Loop through all directories containing pyproject.toml and run poetry update
find . -name "pyproject.toml" -execdir poetry update \;