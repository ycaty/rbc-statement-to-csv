import os
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal, LTTextLineHorizontal, LTChar, LTFigure, LTImage

class statementSplitter():
    def __init__(self,input_folder,output_folder):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.delete_all_files_in_folder(self.output_folder)
        # Destroy current output folder here

    def delete_all_files_in_folder(self,folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path)  # Remove the file or link
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

    def extract_elements_with_positions(self):
        os.makedirs(self.output_folder, exist_ok=True)
        for file_name in os.listdir(self.input_folder):
            if file_name.endswith('.pdf'):
                pdf_path = os.path.join(self.input_folder, file_name)
                base_name = os.path.splitext(file_name)[0]

                for page_layout in extract_pages(pdf_path):
                    output_file = os.path.join(self.output_folder, f'{base_name}_page{page_layout.pageid}.txt')
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(f'Page {page_layout.pageid}\n')
                        for element in page_layout:
                            self.write_element(element, f, indent=0)


    def write_element(self,element, file_handle, indent=0):
        indent_str = ' ' * indent
        if isinstance(element, LTTextBoxHorizontal):
            file_handle.write(f"{indent_str}TextBox: {element.bbox}\n")
            for text_line in element:
                self.write_element(text_line, file_handle, indent + 2)
        elif isinstance(element, LTTextLineHorizontal):
            file_handle.write(f"{indent_str}TextLine: {element.bbox} | Text: {element.get_text().strip()}\n")
            for character in element:
                self.write_element(character, file_handle, indent + 4)
        elif isinstance(element, LTChar):
            file_handle.write(f"{indent_str}Character: {element.bbox} | Text: {element.get_text().strip()}\n")
        elif isinstance(element, LTFigure):
            file_handle.write(f"{indent_str}Figure: {element.bbox}\n")
            for child in element:
                self.write_element(child, file_handle, indent + 2)
        elif isinstance(element, LTImage):
            file_handle.write(f"{indent_str}Image: {element.bbox}\n")
        else:
            file_handle.write(f"{indent_str}Unknown element: {element}\n")


