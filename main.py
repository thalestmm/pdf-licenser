from datetime import datetime
from typing import Optional

import os
from pypdf import PdfReader, PdfWriter
from fpdf import FPDF
from fpdf.enums import YPos

import logging
logger = logging.getLogger(__name__)

# TODO: Turn this into a standalone importable package
# TODO: Add CLI tooling (receive params from cl) -> Maybe create another file?

class PdfLicenseWriter():
    def __init__(self, filepath: Optional[str] = None, client_name: Optional[str] = None,
                 client_cpf: Optional[str] = None, file_name: Optional[str] = None,
                 position: Optional[str] = None) -> None:
        # TODO: Add position default values (left/right/center etc)

        self.filepath = filepath
        self.client_name = client_name
        self.client_cpf = client_cpf

        if file_name is not None:
            self.file_name = file_name
        else:
            self.file_name = "EXPORT"

        try:
            self.reader = PdfReader(self.filepath)
        except:
            raise Exception("File not found under \'{}\'".format(filepath))

    def read_metadata(self) -> None:
        search_dict = {
            "Name": "/LicensedToName",
            "CPF": "/LicensedToCPF",
            "Expedition Date": "/ExpeditionDate",
        }

        try:
            for key, value in search_dict.items():
                print("{} - {}".format(key, self.reader.metadata[value]))

            # TODO: Return values as dict or json
        except:
            raise Exception("No license data found")

    def instantiate_writer(self) -> None:
        self.writer = PdfWriter()

        for page in self.reader.pages:
            self.writer.add_page(page)

    def wipe_metadata(self) -> None:
        if self.reader.metadata is not None:
            logger.info("No metadata found on file")

        self.writer.add_metadata({
            "status": "wiped"
        })

        with open("{}_wiped".format(self.file_name), 'wb') as f:
            self.writer.write(f)


    def write_metadata(self, add_old_metadata: bool = True) -> None:
        # Import existing metadata
        if self.reader.metadata is not None and add_old_metadata:
            self.writer.add_metadata(self.reader.metadata)

        time = datetime.now() # TODO: Adjust this format

        if self.client_name is None or self.client_cpf is None:
            raise Exception("No client information provided.")

        self.writer.add_metadata(
            {
                "/LicensedToName": self.client_name,
                "/LicensedToCPF": self.client_cpf,
                "/ExpeditionDate": time,
            }
        )

    def generate_license_page(self, dimensions: tuple[float,float], position: Optional[str] = None) -> None:
        pdf = FPDF()
        pdf.set_font("Helvetica", size=8)
        pdf.add_page(format=(dimensions[0],dimensions[1]))

        pdf.cell(
            text="Este material foi licenciado para **{}** - CPF **{}**".format(self.client_name, self.client_cpf),
            markdown=True, new_y=YPos.LAST, center=True
        )

        pdf.output("temp.pdf")

    def write_annotations(self) -> None:
        # Get input file dimensions
        width = self.reader.get_page(0).mediabox.width
        height = self.reader.get_page(0).mediabox.height

        CORRECTION_FACTOR = 2.83464924069

        # Generate new page with license information (per position)
        self.generate_license_page(dimensions = (width/CORRECTION_FACTOR, height/CORRECTION_FACTOR))

        # Overlay both documents (Stamp / Watermark)
        license_stamp = PdfReader("temp.pdf").pages[0]

        for page in self.writer.pages:
            page.merge_page(license_stamp, over=True)


    def full_execution(self) -> None:
        self.instantiate_writer()
        self.write_metadata()
        self.write_annotations()
        
        # Export altered file
        with open("{}_{}.pdf".format(self.file_name, self.client_cpf), "wb") as f:
            self.writer.write(f)
        
        # Erase temp file
        if os.path.exists("temp.pdf"):
            os.remove("temp.pdf")

        # TODO: Return the created file


if __name__ == "__main__":
    lw = PdfLicenseWriter(filepath = "./sample.pdf", client_name = "Thales", client_cpf = "123", file_name = "Livro")
    lw.full_execution()
    rd = PdfLicenseWriter(filepath="./Livro_123.pdf")
    rd.read_metadata()
