import re
from prettytable import PrettyTable
from datetime import datetime
'''
def find_header_columns(lines, shift_amount=3):

Note: Play with shift amount here for column spacings
'''

class RBC_chequing_statements_to_csv():

    def __init__(self):
        print ("RBC Chequing statement to csv")
        self.last_date = ''
    def parse_char_stub(self,line):
        """
        line = line of data such as
        Character: (121.91999999999996, 728.1439, 127.39199999999995, 736.1439) | Text: R

        We parse line into a "stub"
        {'type': 'Character',
            'x0': 44.8801,
             'y0': 338.28810000000004,
              'x1': 49.8241,
               'y1': 346.28810000000004,
    '              text': 'D'}



        """
        pattern = r'Character: \(([^,]+), ([^,]+), ([^,]+), ([^)]+)\) \| Text: (.*)'

        match = re.search(pattern, line)
        if match:
            element_type = 'Character'  # Hardcoded as 'Character' because regex is specific for text
            x0 = float(match.group(1))
            y0 = float(match.group(2))
            x1 = float(match.group(3))
            y1 = float(match.group(4))
            text = match.group(5).strip()

            stub_dict = {
                'type': element_type,
                'x0': x0,
                'y0': y0,
                'x1': x1,
                'y1': y1,
                'text': text
            }
            return stub_dict
        else:
            #print(f'Line did not match regex: {line.strip()}')
            return None

    def group_characters_by_line(self,data):
        # we load in data from file shard
        # We Filter all char_data/ stub's
        # if same y0 cord between different pixel stubs we assume on same line,
        # If different y0 cord value found we assume new line(we create a new list append it to list
        # [[ {stub}, {stub}], [{stub},{stub}]] # Sample of 2 horizontal lines containing 2 characters each.
        # We create a list of lists containing these stubs like so [ [{},{}],[{},{}],[{},{}] ]



        char_data = []
        for line in data:
            stub = self.parse_char_stub(line)
            if stub:
                char_data.append(stub)



        sorted_chars = sorted(char_data, key=lambda x: x['y0'], reverse=True)

        lines = []
        current_line = []
        current_y = None
        tolerance = 1.0  # Tolerance to group characters on the same line

        for char in sorted_chars:
            if current_y is None:
                current_y = char['y0']
                current_line.append(char)
            elif abs(current_y - char['y0']) < tolerance:
                current_line.append(char)
            else:
                lines.append(current_line)
                current_line = [char]
                current_y = char['y0']

        if current_line:
            lines.append(current_line)

        return lines

    def group_column_characters_by_line(self,filtered_columns):
        """
        Groups characters within each column by their lines and prints each line for each column.

        :param filtered_columns: List of lists, where each inner list contains stubs for a specific column.
        :return: List of lists containing lines of stubs for each column.
        """
        all_lines_by_column = []

        for column_index, column in enumerate(filtered_columns):
            # Group characters in this column by lines
            column_lines = self.group_characters_by_line(column)
            all_lines_by_column.append(column_lines)

            # Print each line in the column
            #print(f"Column {column_index + 1}:")
            for line_index, line in enumerate(column_lines):
                text = ''.join(stub['text'] for stub in sorted(line, key=lambda x: x['x0']))
                print(f"  Line {line_index + 1}: {text}")

        return all_lines_by_column

    def filter_stubs_within_table(self,leftmost_stub, rightmost_stub, lines):
        """
        Filters out stubs from the stack that are not within the rectangle defined by
        the leftmost and rightmost stubs of the table.

        :param leftmost_stub: Dictionary containing 'x0' and 'y0' coordinates of the leftmost stub.
        :param rightmost_stub: Dictionary containing 'x1' and 'y1' coordinates of the rightmost stub.
        :param lines: List of lists, where each inner list contains stub dictionaries.
        :return: Filtered stack with only stubs within the table bounds.
        """
        # Extract coordinates of the header
        x0, y0 = leftmost_stub['x0'], leftmost_stub['y0']
        x1, y1 = rightmost_stub['x1'], rightmost_stub['y1']




        # Calculate the line equation parameters
        if x1 == x0:  # Prevent division by zero for vertical line
            slope = float('inf')
        else:
            slope = (y1 - y0) / (x1 - x0)

        intercept = y0 - slope * x0

        def is_within_bounds(stub):
            # Check if the stub is within the x-coordinates of the table
            x = stub['x0']
            if x < x0 or x > x1:
                return False
            # Check if the stub is below the line
            y = stub['y0']
            return y <= (slope * x + intercept)

        filtered_lines = []
        for line in lines:
            filtered_line = [stub for stub in line if is_within_bounds(stub)]
            if filtered_line:
                filtered_lines.append(filtered_line)

        return filtered_lines

    def find_opening_balance(self,lines):

        sig = 'Youropeningbalanceon'
        open_balance = []

        for line in lines:
            text = ""
            linecord = line[0]['y0']
            for stub in line:
                #print (stub)
                text+=stub['text']

            # Check here if our header string exists within this line
            if sig in text:

                splix = text.split(sig).pop()
                open_balance_date_raw = splix.split("$")[0]
                open_balance_value = splix.split("$")[1]

                open_balance_date = datetime.strptime(open_balance_date_raw, "%B%d,%Y").strftime("%d%b")


                open_balance = [open_balance_date,open_balance_value]

                return open_balance
        return open_balance
    def find_header(self,lines,shift_amount=3):
        '''


        Sample list returned [bool,dict,dict]
        [True,{'type': 'Character', 'x0': 44.8801, 'y0': 338.28810000000004, 'x1': 49.8241, 'y1': 346.28810000000004,
        'text': 'D'},
        {'type': 'Character', 'x0': 590.605344288, 'y0': 338.28810000000004, 'x1': 593.085344288,
        'y1': 346.28810000000004, 'text': ')'}]

        '''
        lefty,righty = {},{}
        sig = "DateDescriptionWithdrawals($)Deposits($)Balance($)"
        for line in lines:
            text = ""
            # linecord = line[0]['y0']
            for stub in line:
                #print (stub)
                text+=stub['text']

            # Check here if our header string exists within this line
            if sig in text:
                print ("found header line!")
                print (line)
                lefty = line[0]
                righty = line[-1]

                lefty['x0'] -= shift_amount
                righty['x1']+= shift_amount
                return [True,lefty,righty]
        return [False,lefty,righty]

    def find_header_columns(self,lines, shift_amount=1):
        columns = []
        got_header = False
        headers = ["Date", "Description", "Withdrawals($)", "Deposits($)", "Balance($)"]

        for line in lines:
            text = ""
            linecord = line[0]['y0']
            for stub in line:
                text += stub['text']

            # Check here if our header string exists within this line
            if all(header in text for header in headers):
                header_start_indices = [text.find(header) for header in headers]

                for i, header in enumerate(headers):
                    start_index = text.find(header)
                    header_stub = line[start_index]

                    if i < len(headers) - 1:
                        next_start_index = text.find(headers[i + 1])
                        next_header_stub = line[next_start_index]

                        # Apply shift_amount to columns except the first and last
                        if i > 0:  # Avoid shifting the first column
                            header_stub['x0'] -= shift_amount
                        if i < len(headers) - 1:  # Avoid shifting the last column
                            next_header_stub['x0'] -= shift_amount

                        columns.append((header_stub['x0'], next_header_stub['x0']))
                    else:
                        rightmost_stub = line[-1]
                        columns.append((header_stub['x0'], rightmost_stub['x1']))

                return columns

        return columns


    def filter_stubs_by_columns_and_below(self,columns, lines, min_y_threshold=1.0):
        """
        Filters stubs by their column boundaries and ensures they are below a certain vertical threshold.

        :param columns: List of tuples, where each tuple contains the x-coordinates of the left and right bounds of a column.
        :param lines: List of lists, where each inner list contains stub dictionaries.
        :param min_y_threshold: Minimum y-coordinate value for stubs to be included (i.e., stubs must be below this value).
        :return: List of lists, where each inner list contains stubs grouped by columns and below the threshold.
        """
        column_stubs = [[] for _ in range(len(columns))]  # Initialize a list for each column

        def is_within_column_and_below(stub, column):
            x0 = stub['x0']
            x1 = stub['x1']
            y0 = stub['y0']
            col_left, col_right = column
            return (x0 >= col_left and x1 <= col_right) and (y0 >= min_y_threshold)

        for line in lines:
            for stub in line:
                if stub['y0'] >= min_y_threshold:  # Only consider stubs below the threshold
                    # Determine the column the stub belongs to
                    for idx, column in enumerate(columns):
                        if is_within_column_and_below(stub, column):
                            column_stubs[idx].append(stub)
                            break  # Stop checking after finding the column

        return column_stubs

    def detect_intofint_pattern(self,line_data):
        pattern = re.compile(r'^\d+of\d+$')
        return all(line_data.get(f'Column {i}', 'NA') == 'NA' for i in range(2, 5)) and pattern.match(line_data.get('Column 5', ''))

    def detect_last_line(self,line_data):
        return (line_data.get('Column 2') == 'ClosingBalance' and
                line_data.get('Column 3', 'NA') == 'NA' and
                line_data.get('Column 4', 'NA') == 'NA' and
                'Column 5' in line_data)


    def printy_line(self,line):
        text2 = ""
        print("Line details:")
        for stub in line:
            # print(f"Text: {stub['text']}, x0: {stub['x0']}, y0: {stub['y0']}")
            # linecord = line[0]['y0']

            text2 += stub['text']
        print(text2)

    def parse_lines(self,lines):
        '''Display lines of text fetched from lines stack with spaces between words.
        lines = [ [{},{},{}], [{},{},{}], [{}, {}]  ]
        '''
        for line in lines:
            text = ""
            if not line:
                continue
            # Sort the line by x0 coordinate to ensure characters are in order
            line = sorted(line, key=lambda stub: stub['x0'])

            # Iterate through the characters in the line
            for i in range(len(line)):
                current_stub = line[i]
                text += current_stub['text']

                # If not the last character, check the space to the next character
                if i < len(line) - 1:
                    next_stub = line[i + 1]
                    # Determine if there is a space between the current and next character
                    if next_stub['x0'] - current_stub['x1'] > 1.0:  # Threshold for space, can be adjusted
                        text += " "
            print(text)

    def fill_missing_dates(self,combined_data):
        last_date = None
        if combined_data[0]['Column 1'] == 'NA':
            combined_data[0]['Column 1'] = self.last_date

        for entry in combined_data:
            # Check if 'Column 1' is NA
            if entry['Column 1'] == 'NA':
                # Replace 'NA' with the last known date
                if last_date:
                    entry['Column 1'] = last_date
            else:
                # Update the last known date
                last_date = entry['Column 1']

        return combined_data

    def combine_column_lines_and_filter_lines(self,column_lines, filter_lines,opening_balance):
        """
        Combine column lines data with filtered lines to get a complete view of characters per column and row.
        Print the combined data with PrettyTable for testing purposes.

        :param column_lines: List of lists, where each inner list contains stubs for a specific column.
        :param filter_lines: List of lists, where each inner list contains stubs representing lines in the table.
        """
        combined_data = []

        # Iterate through lines
        for line_index, line in enumerate(filter_lines):
            # Create a dict to hold characters for the current line across all columns
            line_data = {}
            for column_index, column in enumerate(column_lines):
                # Filter stubs that belong to the current column
                column_stubs = [stub for stub in column if stub in line]

                # Create a list of texts for the current column in this line
                column_texts = ''.join(stub['text'] for stub in sorted(column_stubs, key=lambda x: x['x0']))
                line_data[f'Column {column_index + 1}'] = column_texts or 'NA'

            combined_data.append(line_data)

        # Create and print the PrettyTable
        headers = [f'Column {i + 1}' for i in range(len(column_lines))]
        table = PrettyTable(headers)
        last_line = None
        if combined_data[0] == {'Column 1': 'Date', 'Column 2': 'Description', 'Column 3': 'Withdrawals($)',
                                'Column 4': 'Deposits($)', 'Column 5': 'Balance($)'}:
            combined_data.pop(0)
            print("popped header")

        if combined_data[0]['Column 2'] == 'OpeningBalance':
            combined_data[0]['Column 1'] = opening_balance[0]

        combined_data = self.fill_missing_dates(combined_data)

        combined_data_2 = []

        for line_data in combined_data:
            #print(line_data)
            if self.detect_intofint_pattern(line_data):
                #print("Detected 'intofint' pattern, breaking loop.")
                break
            if self.detect_last_line(line_data):
                #print("Detected 'ClosingBalance' line, saving as last line.")
                last_line = line_data
                table.add_row([last_line.get(header, 'NA') for header in headers])
                break


            combined_data_2.append(line_data)
            table.add_row([line_data.get(header, 'NA') for header in headers])

        self.last_date = combined_data[-1]['Column 1']


        print(table)
        return combined_data_2

