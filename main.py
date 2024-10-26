from datetime import datetime
from typing import Optional

from pypdf import PdfReader, PdfWriter

# TODO: Turn this into a standalone importable package

class PdfLicenseWriter():
    def __init__(self, filepath: Optional[str] = None, client_name: Optional[str] = None,
                 client_cpf: Optional[str] = None, file_name: Optional[str] = None,
                 position: Optional[str] = None):
        # TODO: Add position default values (left/right/center etc)
        # TODO: Add CPF formatting XXX.XXX.XXX-XX on visible text box (?)

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
        if self.reader.metadata is not None:
            print(self.reader.metadata)
        else:
            print("No metadata found")

    def instantiate_writer(self) -> None:
        self.writer = PdfWriter()

        for page in self.reader.pages:
            self.writer.add_page(page)

    def write_metadata(self, add_old_metadata: bool = True):
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

    def full_execution(self) -> None:
        self.instantiate_writer()
        self.write_metadata()

        with open("{}_{}.pdf".format(self.file_name, self.client_cpf), "wb") as f:
            self.writer.write(f)


if __name__ == "__main__":
    lw = PdfLicenseWriter(filepath = "./sample.pdf", client_name = "Thales", client_cpf = "123", file_name = "Livro")
    lw.full_execution()
    lw = PdfLicenseWriter(filepath = "./Livro_123.pdf")
    lw.read_metadata()
