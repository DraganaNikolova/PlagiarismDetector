from glob import glob
import re
import os
import win32com.client as win32
from win32com.client import constants
import os
import zipfile
from docx import Document
import json
import base64
from os.path import basename
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from bs4 import BeautifulSoup


def extractFromDirectory(directory):
    for filename in os.scandir(directory):
        if filename.is_file() and filename.path.endswith(".doc"):
            save_as_docx(filename.path)
        elif filename.is_file() != True: extractFromDirectory(filename.path)
    
    return docFiles


def save_as_docx(path):
    # Opening MS Word
    word = win32.gencache.EnsureDispatch('Word.Application')
    doc = word.Documents.Open(path)
    doc.Activate ()

    # Rename path with .docx
    new_file_abs = os.path.abspath(path)
    new_file_abs = re.sub(r'\.\w+$', '.docx', new_file_abs)

    # Save and Close
    word.ActiveDocument.SaveAs(
        new_file_abs, FileFormat=constants.wdFormatXMLDocument
    )
    doc.Close(False)


def extractFromDirectory(directory, zips):
    for filename in os.scandir(directory):
        if filename.is_file() and (filename.path.endswith(".docx") or filename.path.endswith(".doc")):
            continue
        if zipfile.is_zipfile(filename.path):
            zips.append(filename.path)
        elif filename.is_file() != True: extractFromDirectory(filename.path, zips)
    
    return zips


def getMetaData(doc, author, category, comments, content_status, created, identifier, keywords, last_modified_by, language, modified, revision, subject, title, version, last_printed):
    metadata = {}
    prop = doc.core_properties
    author.append(prop.author)
    category.append(prop.category)
    comments.append(prop.comments)
    content_status.append(prop.content_status)
    created.append(prop.created)
    identifier.append(prop.identifier)
    keywords.append(prop.keywords)
    last_modified_by.append(prop.last_modified_by)
    language.append(prop.language)
    modified.append(prop.modified)
    revision.append(prop.revision)
    subject.append(prop.subject)
    title.append(prop.title)
    version.append(prop.version)
    last_printed.append(prop.last_printed)
    
    return author, category, comments, content_status, created, identifier, keywords, last_modified_by, language, modified, revision, subject, title, version, last_printed


def extractStudentNames():
    # Extracting names from filenames
    df['filePath']

    list = []
    for fileName in df['filePath']:
        parts = fileName.split("\\")
        nameFolder = parts[-2]
        nameStudent = nameFolder.split("_")[0]
        
        if 'Unzip' in fileName:
            nameFolder = parts[-4]
            nameStudent = nameFolder.split("_")[0] 
        list.append(nameStudent)
        
    df['nameStudent'] = list

def get_linked_text(file_name):

    try:
        archive = zipfile.ZipFile(file_name, "r")
        file_data = archive.read("word/document.xml")
        soup = BeautifulSoup(file_data, "xml")
    except:
        return []
    links = []

    # This kind of link has a corresponding URL in the _rel file.
    for tag in soup.find_all("hyperlink"):
        # try/except because some hyperlinks have no id.
        try:
            links.append(tag.text)
        except:
            pass

    # This kind does not.
    for tag in soup.find_all("instrText"):
        # They're identified by the word HYPERLINK
        if "HYPERLINK" in tag.text:
            # Get the URL. Probably.
            try:
                url = tag.text.split('"')[1]
            except:
                continue

            # The actual linked text is stored nearby tags.
            # Loop through the siblings starting here.
            temp = tag.parent.next_sibling
            text = ""

            while temp is not None:
                # Text comes in <t> tags.
                maybe_text = temp.find("t")
                if maybe_text is not None:
                    # Ones that have text in them.
                    if maybe_text.text.strip() != "":
                        text += maybe_text.text.strip()

                # Links end with <w:fldChar w:fldCharType="end" />.
                maybe_end = temp.find("fldChar[w:fldCharType]")
                if maybe_end is not None:
                    if maybe_end["w:fldCharType"] == "end":
                        break

                temp = temp.next_sibling

            links.append(text)

    return links


def extract_text(filename):
    filename = r"C:\Users\stoja\Desktop\Text Processing\Ке-20202021Z-36_13290-Место за вашиот дневник-88411\Александар Максимов_13532805_assignsubmission_file_\ Александар Максимов 161255.docx"
    doc = Document(filename)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)

    fullText = '\n'.join(fullText)
    return fullText
    

def clean_text(text):
    '''Make text lowercase, remove \n, (, remove text between brackets, remove punctation, 
    remove non-sensical text, remove multiple spaces'''
    text = text.lower()
    text = re.sub('\n', ' ', text)
    text = re.sub(r'[(]', ' ', text)
    text = re.sub('\[.*?\]', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub(r'[^\w]', ' ', text)
    text = re.sub(' +', ' ', text)
    
    return text

