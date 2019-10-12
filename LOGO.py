import fitz                          # <-- PyMuPDF
from pathlib import Path
from errors_PFD import  log_text
from configparser import ConfigParser
import sys
import traceback
import os

def add_picture(path_pdf,path_picture, position_x, position_y, page_height):
    try:
        doc = fitz.open(path_pdf)          # open the PDF
        rect = fitz.Rect(position_x, position_y+20, position_x+100, position_y+90)     # where to put image: use upper left corner

        page = doc[0]
        page._wrapContents()
        
        page.insertImage(rect, filename =  path_picture)
        
        doc.saveIncr()
    
    except ValueError as e:
        log_text(traceback.format_exc())



