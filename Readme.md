# Zotero Library Parser

A tool to import all saved PDF files from a cloud-synced Zotero library, then auto parse them with Python and save as utf8 .txt files plus a .csv with meta-data.

It uses ([pyzotero](https://github.com/urschrei/pyzotero)) and ([pdfminer](https://pypi.org/project/pdfminer/)) to import and parse the pdfs.

The parsed texts are saved in the folder "texts" (create it if you don't have it). They are named after their Zotero IDs, which is also a variable in the meta-data. The meta-data contains *all* entries in the Zotero library but the folder "texts" only contains those entires that have a PDF attachment that is longer than 200 characters and did not have an exit exception during the parsing. 

## Background

This parser is a simple derivative of coding work done as part of the ([bibfilter app](https://gitlab.com/mx.tom/bibfilter)), developed in the German Science Foundation funded project "The Reciprocal Relationship of Public Opinion and Social Policy" ([BR 5423/2-1](https://www.socium.uni-bremen.de/projects/?proj=614)). 

Its intended application is to parse files for the ([Replication Wiki](https://replication.uni-goettingen.de/)) to help train a machine to update the RepWiki and to use for teaching purposes for students learning to do natural language processing.

## User Notes

The coding here is basic. The file get_pdfs_zot.py can be run after installing the necessary packages in Python - these dependencies are listed in commented out pip install command lines at the top of the file. For this to run properly the user needs to create a file 'keys.py'. This is where the Zotero group library name and API key are stored, in addition to sub-folder names if desired. There is a 'key_example.py' file to demonstrate how to create the 'keys.py' file.

## Debugging

Ensure that items in Zotero are not themselves PDFs and have all necessary information in them.


