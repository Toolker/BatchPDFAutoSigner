import sys
from errors_PFD import log_text
from OpenSSL.crypto import load_pkcs12
from endesive import pdf
from datetime import datetime
from datetime import timezone
from configparser import ConfigParser
from os import listdir
from os.path import isfile, join
import time
from PyPDF2 import PdfFileReader, PdfFileWriter, utils
from LOGO import add_picture
import os.path
import shutil
import traceback
from tkinter import messagebox

def check_pdf_names(PDF_source,PDF_destination,pdf_file):
    first_PDF_source=os.path.join(PDF_source, pdf_file)
    new_path=PDF_destination
    new_destination_file_path=os.path.join(PDF_destination, pdf_file)

    while os.path.isfile(new_destination_file_path):
        first_split = pdf_file.split('({}')
        if len(first_split)==2:
            first_part_split = first_split[0]
            secont_part_split = first_split[1]
            second_split = secont_part_split.split('{})')
            i = second_split[0]
            i=int(i)
            i=i+1
            i=str(i)
            pdf_file = first_part_split + '({}' + i + '{})'
            pdf_file=pdf_file+".pdf"
        else:
            pdf_file=pdf_file.split(".pdf")

            pdf_file=pdf_file[0]

            pdf_file=pdf_file+'({}1{}).pdf'



        new_destination_file_path = os.path.join(new_path, pdf_file)
        print(new_destination_file_path)
    second_PDF_source=os.path.join(PDF_source, pdf_file)

    os.rename(first_PDF_source,second_PDF_source)
    return(pdf_file)

def PDF_sign(target_file):
    contact = bytes(parser.get('CERTIFICATE', 'email'), 'utf-8')
    location = bytes(parser.get('CERTIFICATE', 'city'), 'utf-8')
    name = str(parser.get('TRANSLATIONS', 'entity_name'))
    signaturebox = parser.get('GENERAL', 'signaturebox_position')
    company_name = parser.get('CERTIFICATE', 'company_name')
    lang_digitally_signed = parser.get('TRANSLATIONS', 'digitally_signed_text')
    lang_date = parser.get('TRANSLATIONS', 'date_text')
    signaturebox = [int(k) for k in signaturebox.split(',')]
    #today = date.today()
    today = datetime.now(timezone.utc)
    exact_time_str = today.strftime("%Y%m%d") + "082642+02\'00\'"
    exact_time_str2 = today.strftime("%Y/%m/%d")
    exact_time_bytes = bytes(exact_time_str, 'utf-8')

    pfx_path = parser.get('PATHS', 'certificate_file')
    your_pass = bytes(parser.get('CERTIFICATE', 'password'), 'utf-8')
    try:
        p12 = load_pkcs12(open(pfx_path, 'rb').read(), your_pass)
    except Exception:
        log_text("Opening specified certificate failed. Might be your password.")
        log_text(traceback.format_exc())
        return

    source_file_path = target_file
    destination_file_path = os.path.join(PDF_destination, target_file)

    pdf_file_name = open(source_file_path, 'rb')
    input1 = PdfFileReader(pdf_file_name)
    page_height = int(input1.getPage(0).mediaBox.upperLeft[1])
    pdf_file_name.close()

    signature = bytes(lang_digitally_signed +" "+ name + ". " + lang_date + ": " + exact_time_str2, 'utf-8')

    dct = {
        b'sigflags': 3,
        b'contact': contact,
        b'location': location,
        b'signingdate': exact_time_bytes,
        b'reason': b'null',
        b'signature': signature,
        b'company': company_name,
        b'signaturebox': (
        signaturebox[0], page_height - signaturebox[1], signaturebox[0] + 100, page_height - signaturebox[1] - 50),
    }

    ### put your_signature_image_or_logo
    your_signature_image_or_logo = parser.get('PATHS', 'signature_image_or_logo_file')
    if os.path.isfile(your_signature_image_or_logo):
        add_picture(source_file_path, your_signature_image_or_logo, signaturebox[0], signaturebox[1], page_height)

    datau = open(source_file_path, 'rb').read()
    datas = pdf.cms.sign(datau, dct,
                         p12.get_privatekey().to_cryptography_key(),
                         p12.get_certificate().to_cryptography(),
                         [],
                         'sha256')

    with open(destination_file_path, 'wb') as fp:
        fp.write(datau)
        fp.write(datas)
        fp.close()


def pdf_recompile(target_file):
    # we will read the content and rewrite it next the the python file, then we will move it back
    source_file_path = os.path.join(PDF_source, target_file)
    pdf = PdfFileReader(source_file_path)
    pdf_writer = PdfFileWriter()

    for page in range(pdf.getNumPages()):
        pdf_writer.addPage(pdf.getPage(page))

    with open(target_file, 'wb') as out:
        pdf_writer.write(out)
        out.close()

    log_text(target_file + ": recompiled - OK")


def pdf_clean(target_file):
    os.remove(target_file)
    source_file_path = os.path.join(PDF_source, target_file)
    destination_file_path = os.path.join(PDF_destination, target_file)

    pdf_is_readable = True
    try:
        pdf_file = open(destination_file_path, "rb")
        pdf = PdfFileReader(pdf_file)
        first_page = pdf.getPage(0)
        page_text = first_page.getContents()
        pdf_file.close()
    except Exception:
        log_text(destination_file_path + " Corrupted - NOT OK!    ERROR:")
        log_text(traceback.format_exc())
        pdf_is_readable = False

    
    log_text(destination_file_path + " Signature OK!")
    os.remove(source_file_path)
    
    

parser = ConfigParser()
parser.read('config.ini')

try:
    time_in_seconds = int(parser.get('GENERAL', 'time_to_restart_in_seconds'))
except ValueError as e:
    log_text(traceback.format_exc())


pfx_path = parser.get('PATHS', 'certificate_file')
your_pass = bytes(parser.get('CERTIFICATE', 'password'), 'utf-8')
try:
    p12 = load_pkcs12(open(pfx_path, 'rb').read(), your_pass)
except Exception:
    messagebox.showerror("Certificate Error", "Opening specified certificate failed. Might be the path or the password you provided. Please check config and retry.")
    exit(-1)

PDF_source = parser.get('PATHS', 'pdf_source_folder')
PDF_destination = parser.get('PATHS', 'pdf_destination_folder')
your_signature = parser.get('PATHS', 'certificate_file')
####  CHECK IF THERE ARE ANY PDF TO SIGN


while True:
    try:
        only_pdf_files = [f for f in listdir(PDF_source)
                          if (isfile(join(PDF_source, f))) & (f.lower().endswith('.pdf'))]

        for pdf_file in only_pdf_files:
            pdf_file=str(check_pdf_names(PDF_source,PDF_destination,pdf_file))
            pdf_recompile(pdf_file)
            PDF_sign(pdf_file)
            pdf_clean(pdf_file)


    except FileNotFoundError as e:
        log_text(traceback.format_exc())

    except FileExistsError as e:
        log_text(traceback.format_exc())

    time.sleep(time_in_seconds)
