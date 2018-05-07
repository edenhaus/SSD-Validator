# SSD-Validator

Validator for submissions in the course Semi-Structured Data, Vienna University of Technology.

## Requirements

Python 3

## Setup

Most of the setup (setting up the directory structure) is done by the script itself.

## Usage

* Start the script via `python3 validatorScript.py` to create the directory infrastructure
* Copy the sample (unzipped) solution files into the directory `solution/`
* Copy the submission ZIP file into the directory `download/`
* Extract and validate the submission via `python3 validatorScript.py --extract`

After validation, the submission ZIP will be placed in the directory `validated/`.

A detailed overview over the accepted command-line arguments can be viewed by passing the `--help` argument.