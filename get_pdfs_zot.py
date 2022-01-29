#pip install pyzotero
#pip install PyPDF2
#pip install pdfminer.six
#pip install pandas
#mkdir("texts") #if the directory doesn't already exist

import os
from io import BytesIO
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
from PyPDF2 import PdfFileReader
from pyzotero import zotero, zotero_errors
import pandas as pd

# run keys.py to get keys (this file has to be created by user, it is currently blocked by .gitignore)
exec(open('keys.py').read())

zot = zotero.Zotero(libraryID, 'group', APIkey)

items = None

# empty list of article attributes
list_article_attributes = []

# Retrieve limit=X zotero articles, max 100
#items = zot.top(limit=)
## Or all articles, this may take a while
items = zot.everything(zot.top())
## or a single collection
#items = zot.everything(zot.collection_items_top(libraryID))

##### Parsing routine
for item in items:
    content="none"
    articleTitle = item['data']['title'] # set attributes for saving the files as
    articleID = item['data']['key'] # set up an attribute of the Zotero internal key ("ID")
    print(f"{articleTitle}")
    print(f"{articleID}")
    if os.path.isfile(os.path.join('texts', f'{articleID}.txt')):
        print("Parsed file already exists")
    else:
        try:
            attachments = zot.children(item['data']['key'])

            # Goes through each attachment if there is any
            for each in attachments:
            ## Executes everything that comes after try, when encountering an error, execute the "except" block and keep running instead of exiting program
                try:
                # Notes are different from attachments and don't have contentType attribute
                    if each["data"]["itemType"] == "attachment":
                        if each["data"]["contentType"] == 'application/pdf':
                            content = "test"
                            pdfID = each["data"]["key"]
                            # Save attachment as pdf
                            zot.dump(pdfID, 'zot_article.pdf')
                            
                            with open('zot_article.pdf', 'rb') as file:
                                pdfFile = PdfFileReader(file)
                                totalPages = pdfFile.getNumPages()
                    
                            # Parse only first 60 pages at maximum
                            totalPages = min(60, totalPages)
                    
                            # Set paramters of extraction
                            laparam = LAParams(detect_vertical=True)
                            # get content of pdf
                            # Parsing over only a few pages seperately may take longer but uses less memory
                            step = 3
                            for pg in range(0, totalPages, step):
                                content += extract_text('zot_article.pdf', page_numbers=list(range(pg, pg+step)), laparams=laparam)
                            #simpler extraction (use for debugging)
                            #content = extract_text('zot_article.pdf', laparams=laparam)
                            #print(content)
                            # Check length of content, exclude entries with less than 200 characters
                            if len(content) < 200:
                                break
                            else:
                                ## Output to file:
                                with open(os.path.join('texts', f'{articleID}.txt'), 'w', encoding="utf-8") as f:
                                    f.write(content)
                                break
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)
        # Print report
        if len(content) > 200:
            print("Extracted content")
        elif content == "none":
            print("No pdf file available")
        else:    
            print(f"Unable to extract content from pdf")
    # print empty line
    print()
    
 
    
##### Meta-data routine
# Get attributes
for item in items:
    # Get Article attributes and make sure to skip KeyError (not all entrytype e.g. journal book etc. have the same attributes)
    content = {"title": "","url":"", "key":"" ,"itemType":"", "DOI": "", "ISSN":"", "publicationTitle":"","journalAbbreviation":"","abstractNote":"","pages":"","language":"","volume":"",
    "issue":"","dateAdded":"","dateModified":"","ISBN":"", "numPages":"", "subcol_0":"", "subcol_1":"", "subcol_2":"", "subcol_3":""}
    for key in content:
        k = False
        try:
            content[key] = item["data"][key]
        except Exception as e:
            pass

    # Get year        
    try:
        itemYear = item["meta"]["parsedDate"].split("-")[0]
    except Exception as e:
        itemYear = ""

    # Convert author names to a sensible format
    author, authorlast = "", ""
    try:
        for dic in item["data"]["creators"]:
            try:
                # Entriers without firstName use "name", otherwise firstName and lastName
                if "name" in dic:
                    if len(authorlast) > 0:
                        authorlast += "; " + dic["name"]
                    else:
                        authorlast = dic["name"]
                    if len(author) > 0:
                        author += "; " + dic["name"]
                    else:
                        author = dic["name"]

                else:
                    if len(authorlast) > 0:
                        authorlast += "; " + dic["lastName"]
                    else:
                        authorlast = dic["lastName"]

                    if len(author) > 0:
                        author += "; " + dic["lastName"] + ", " + dic["firstName"]
                    else:
                        author = dic["lastName"] + ", " + dic["firstName"]
            except Exception as e:
                pass
    except Exception as e:
        pass
    # get subcollection keys
    try:
        content["subcol_0"] = item['data']['collections'][0]
    except Exception as e:
        pass
    try:
        content["subcol_1"] = item['data']['collections'][1]
    except Exception as e:
        pass
    try:
        content["subcol_2"] = item['data']['collections'][2]
    except Exception as e:
        pass
    try:
        content["subcol_3"] = item['data']['collections'][3]
    except Exception as e:
        pass
            
    # Create a dictionary with all the attributes
    currentArticle = {"title":content["title"], 
                        "url":content["url"],
                        "ID":content["key"], 
                        "type":content["itemType"],
                        "author":author,
                        "authorlast":authorlast, 
                        "year":itemYear, 
                        "doi":content["DOI"],
                        "issn":content["ISSN"],
                        "isbn":content["ISBN"],
                        "publication":content["publicationTitle"],
                        "journal":content["publicationTitle"] if not content["itemType"].startswith("book") else "",
                        "booktitle":content["publicationTitle"] if content["itemType"].startswith("book") else "",
                        "journal_abbrev":content["journalAbbreviation"],
                        "abstract":content["abstractNote"],
                        "pages":content["pages"] if content["pages"] != "" else content["numPages"],
                        "language":content["language"],
                        "volume":content["volume"], 
                        "number":content["issue"],
                        "subcol_0":content["subcol_0"],
                        "subcol_1":content["subcol_1"],
                        "subcol_2":content["subcol_2"],
                        "subcol_3":content["subcol_3"],}
    
    list_article_attributes.append(currentArticle)


# Convert List of dictionaries of article stats to dataframe using the pandas library
df = pd.DataFrame(list_article_attributes)

# replace Zotero folder keys with Zotero folder names
# Remember! This has to be defined as a dictionary by the user in a file called keys.py
df['subcol_0'] = df['subcol_0'].replace(subcol, regex=True)
df['subcol_1'] = df['subcol_1'].replace(subcol, regex=True)
df['subcol_2'] = df['subcol_2'].replace(subcol, regex=True)
df['subcol_3'] = df['subcol_3'].replace(subcol, regex=True)

df.to_csv('data.csv')
#print(df)
