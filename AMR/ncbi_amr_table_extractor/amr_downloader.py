import requests
import json
import argparse
import os

import sys
from lxml import html


def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    """
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


def json_field(value):
    """
    Replace spaces with _ and turn value to lowercase
    :param value: the value to transform 
    :return the json value
    """
    return value.replace(" ", "_").lower()


def run(last_accession, input_file, output_folder ):
    """
    This is the main process
    :param last_accession: if you want to recover the process from the last accession processed
    :param input_file: the file from which the acessions are extracted to query NCBI
    :param output_folder: the output folder of the result files
    """
    unsuccesful = []
    with open(input_file, "r") as fin:
        sample_ids = [line.strip() for line in fin.readlines()]

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    start_index = 0
    total_samples = len(sample_ids)
    if last_accession:
        start_index = sample_ids.index(last_accession)
        sample_ids = sample_ids[start_index::]
        
    print_progress(iteration=start_index, total=total_samples, prefix="Initializing")
    for (i, ncbi_sample) in enumerate(sample_ids, start_index+1):

        # get ncbi sample page
        url = "https://www.ncbi.nlm.nih.gov/biosample/?term={}".format(ncbi_sample)
        page = requests.get(url)
        if not page.status_code == requests.codes.ok:
            unsuccesful.append(ncbi_sample)
            continue

        # retrieve antibiogram table
        tree = html.fromstring(page.content)
        amr_table = tree.xpath("//table[caption = 'Antibiogram']")
        amr_json_table = []

        if amr_table:
            amr_table = amr_table[0]
            amr_table_headers = [json_field(value) for value in amr_table.xpath(".//th/text()")]
            amr_table_rows = amr_table.xpath("tr")
            for row in amr_table_rows:
                amr_row_values = [td.text if td.text else "" for td in row.xpath("td")]
                # A lot of fields in the measurement are actually in a format
                # not compatible with number (e.g. 4/76, 4/2)
                # Check for example sample 4549305 for an example
                amr_row_object = dict(zip(amr_table_headers, amr_row_values))
                amr_json_table.append(amr_row_object)

            # store amr table to disk
            with open("{}/{}_table.json".format(output_folder, ncbi_sample), "w") as fop:
                json.dump(amr_json_table, fp=fop)
                print_progress(iteration=i, total=total_samples, 
                    prefix="Completed {}".format(ncbi_sample))

    if unsuccesful:
        with open('{}/unsuccesful.txt'.format(output_folder), 'w') as fout:
            fout.writelines(unsuccesful)
            print("Some samples were not retrieved, check unsuccesful.txt file for accession")


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--accessions", default="ncbi_accessions.txt", 
        help="a file containing a list of ncbi biosamples accession, one per line")
    arg_parser.add_argument("--output", default="files", 
        help="the destionation folder for all the exported table")
    arg_parser.add_argument("--first_acc", default="",
        help="the accession to start from. Need to be one of the provided list")
    args = arg_parser.parse_args()

    run(last_accession=args.first_acc, input_file=args.accessions, output_folder=args.output)
