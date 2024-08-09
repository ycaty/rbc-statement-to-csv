from RBC_CHECK_STAETMENT_TO_CSV import RBC_chequing_statements_to_csv
import unicodecsv as csv
import os
from statement_splitter import statementSplitter
# Come up with seperate page logics
# OpeningBalance date fetcher
# Logic for Column dates (Previous files needed for this?
# Remove header stuff for each file from stack date description etc
# Folder logic (incase dont exist)
# Clean up code


import csv

def write_combined_data_to_csv(combined_data, file_path):
  """
  Writes combined data (a list of dictionaries) to a CSV file.

  Args:
    combined_data: A list of dictionaries, where each dictionary represents a row of data.
    file_path: The path to the CSV file to write to.
  """

  with open(file_path, 'a', newline='') as csvfile:
    fieldnames = combined_data[0].keys()  # Assuming all dicts have the same keys
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    if csvfile.tell() == 0:  # Check if file is empty
      writer.writeheader()

    writer.writerows(combined_data)



## Add function here to check folder paths


# Specify the input folder and output folder
input_folder = 'statements'
output_folder = 'outputFolder'
output_file = "loot_output.csv"


statementSplix = statementSplitter(input_folder,output_folder)

# Extract elements and save to the output folder
statementSplix.extract_elements_with_positions()

opening_balance = []
rbc_tool = RBC_chequing_statements_to_csv()
statement_files = os.listdir('outputFolder')


for statement_filename in statement_files:
    # Load Cord Data from statement File
    statement_shard = "outputFolder/" + statement_filename
    #Load data from cord file statement_splitter.py
    with open(statement_shard, "r") as f:
        data = [x.strip() for x in f.readlines()]

    # Generate lines stack containing list of lists with stubs(pixel values + character values)
    # Converts lines from files into dict stubs
    lines = rbc_tool.group_characters_by_line(data)

    if "_page1" in statement_filename:
        # Returns ['date','$123.25']
        opening_balance = rbc_tool.find_opening_balance(lines)
        print (opening_balance)

    # Get lefty and righty most pixel stub values got_header returns [bool,{lefty pixel of header},{righty pixel of header}}
    got_header = rbc_tool.find_header(lines)

    # 'type': 'Character', 'x0': 16.8, 'y0': 634.9277, 'x1': 21.744, 'y1': 642.9277, 'text': 'D'}


    if got_header[0]:
        # Filter out all lines below lefty/righty most pixels of header
        filter_lines = rbc_tool.filter_stubs_within_table(got_header[1],got_header[2],lines)

        # Fetch header column pixels for each header
        header_columns = rbc_tool.find_header_columns(lines,shift_amount=1)

        # Use header_columns and filtered_lines to create filtered columns
        filtered_columns = rbc_tool.filter_stubs_by_columns_and_below(header_columns, filter_lines)

        # rbc_tool.parse_lines(lines) # May need this in future

        combined_data = rbc_tool.combine_column_lines_and_filter_lines(filtered_columns,filter_lines,opening_balance)
        print (" above found from ", statement_filename)

        write_combined_data_to_csv(combined_data,output_file)

