# Written in python3.8
# Uses prettytable (pip install prettytable)

# rbc-statement-to-csv
Folders needed 
/outputFolder
/statements

Place rbc chequing files into statements folder ( Note: data will be read chronologically from statements to stack, best to keep .pdf names same as when downloaded from rbc)

# Specify the input folder and output folder
input_folder = 'statements' # We place our rbc statement files here
output_folder = 'outputFolder' # This will be used for splitting purposes
output_file = "loot_output.csv" # This is the main file

