# Antibiogram NCBI Biosample scraper

Given a set of NCBI Biosample ids, this script check the corresponding html page for antibiogram table, storing it as a JSON file
in a separate folder

In order to run this script you need some dependencies. To sort this out quickly, the use of [pipenv](https://docs.pipenv.org/) is encouraged. Follow the tutorial on pipenv site to install pipenv, or provide the dependencies for the script by yourself.

To create a virtualenv and install the dependencies do:
```shell
pipenv install --three
```
*Note*: The file is written in **Pyhton 3**

To activate the virtual environment do:
```shell
pipenv shell
```

For information about the script, just use the `--help` command:

```shell
python amr_downloader.py --help
```

The script can be run without any paramters, it will read the accessions from the `ncbi_accessions.txt` file and store the results in the `files` directory.
If for some reason the process is interrupted, you can provide also a `first_acc` argument to start the extraction process from the corresponding accession.

## AMR json-schema
A draft of the json-schema for AMR data is available [here](https://jsonschemalint.com/#/version/draft-06/markup/json?gist=edcb93c81a6c9ee08bdf54ade4fd8f49)
