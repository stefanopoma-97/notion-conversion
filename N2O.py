# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 13:34:37 2020

@author: books
"""

from os import makedirs, path
from re import compile
from shutil import copyfileobj, make_archive
from zipfile import ZipFile
from pathlib import Path
import N2Omodule
from tempfile import TemporaryDirectory
import tkinter as tk
from tkinter import filedialog
import os
import re
#from easygui import fileopenbox

#NotionZip = Path(fileopenbox(filetypes = ['*.zip']))

def open_zip_file():
    global selected_zip_file
    file_path = filedialog.askopenfilename(filetypes=[("File ZIP", "*.zip")])
    if file_path:
        selected_zip_file = file_path
        print("File ZIP selezionato:", selected_zip_file)
        root.destroy()  # Chiudi la finestra di dialogo

# Creazione dell'interfaccia utente
root = tk.Tk()
root.title("Seleziona un file ZIP")

selected_zip_file = None  # Variabile per memorizzare il percorso del file ZIP selezionato

# Creazione di un pulsante per aprire il dialogo di selezione del file ZIP
open_button = tk.Button(root, text="Seleziona file ZIP", command=open_zip_file)
open_button.pack(pady=20)

# Avvio dell'interfaccia utente
root.mainloop()

# Dopo la chiusura della finestra, puoi utilizzare la variabile "selected_folder"
if selected_zip_file:
    print("Percorso della cartella selezionata:", selected_zip_file)
    # Puoi aggiungere ulteriori azioni da eseguire con il percorso della cartella selezionata qui.



# Load zip file
#notionsData = ZipFile(NotionZip, 'r')
notionsData = ZipFile(selected_zip_file, 'r')
NotionZip = Path(selected_zip_file)


NotionPathRaw = []
ObsidianPathRaw = []
NotionPaths = []
ObsidianPaths = []



# Generate a list of file paths for all zip content
[NotionPathRaw.append(line.rstrip()) for line in notionsData.namelist()]

verbose = False
def debug_print(msg):
    if verbose:
        print(msg)

# Clean paths for Obsidian destination
regexUID = compile("\s+\w{32}")
regexForbitCharacter = compile("[<>?:/\|*\"]")

for line in NotionPathRaw:
    ObsidianPathRaw.append(regexUID.sub("", line))


### PATHS IN PROPER OS FORM BY PATHLIB ###
[NotionPaths.append(Path(line)) for line in NotionPathRaw]
[ObsidianPaths.append(Path(line)) for line in ObsidianPathRaw]



# Get all the relevant indices (folders, .md, .csv, others)
mdIndex, csvIndex, othersIndex, folderIndex, folderTree = N2Omodule.ObsIndex(ObsidianPaths)

# Rename the .csv files to .md files for the conversion
for i in csvIndex:
    ObsidianPaths[i] = Path(str(ObsidianPaths[i])[0:-3]+"md")


## Create a temporary directory to work with
unzipt = TemporaryDirectory()
tempPath = Path(unzipt.name)


## Create temp directory paths that match zip directory tree
tempDirectories = []

# Construct complete directory paths (<tempDirecory>/<zipDirectories>)
for d in folderTree:
    tempDirectories.append(tempPath / d)

## Create the temporary directory structure for future archive
for d in tempDirectories:
    makedirs(d, exist_ok=True)



num_link = [0, 0, 0, 0]
# Process all MD files
for n in mdIndex:
    
    # Access the original MD file
    with notionsData.open(NotionPathRaw[n], "r") as mdFile:
        
        # Find and convert Internal Links to Obsidian style
        mdContent, cnt = N2Omodule.N2Omd(mdFile)
        num_link = [cnt[i]+num_link[i] for i in range(len(num_link))]
        
        # Exported md file include header in first line
        # '# title of file'
        # Get full file name by first line of exported md file instead file name ObsidianPaths[n]
        ## Make temp destination file path
        new_file_name = mdContent[0].replace('# ', '') + '.md'
        new_file_name = regexForbitCharacter.sub("", new_file_name)
        new_file_name = N2Omodule.clean_file_path(new_file_name)
        newfilepath = tempPath / path.dirname(ObsidianPaths[n]) / os.path.basename(ObsidianPaths[n]) #new_file_name
        newfilepath = tempPath / path.dirname(ObsidianPaths[n]) / new_file_name

        print("new file path:", newfilepath)
        # Check if file exists, append if true
        if path.exists(newfilepath):
            append_write = 'a' # append if already exists
        else:
            append_write = 'w' # make a new file if not
        
        # Save modified content as new .md file
        with open(newfilepath, append_write, encoding='utf-8') as tempFile:
            [print(line.rstrip(), file=tempFile) for line in mdContent]


# Process all CSV files
for n in csvIndex:
    
    # Access the original CSV file
    with notionsData.open(NotionPathRaw[n], "r") as csvFile:
         
        # Convert CSV content into Obsidian Internal Links
        mdTitle = N2Omodule.N2Ocsv(csvFile)

        ## Make temp destination file path
        newfilepath = tempPath / ObsidianPaths[n]

        # Check if the file name ends with "_db" if yes move one level up in the directory and remove "_db"
        if newfilepath.stem.endswith("_db"):
            newfilename = newfilepath.stem[:-3] + newfilepath.suffix
            newparentpath = os.path.dirname(os.path.dirname(newfilepath))  # Move one level up in the directory
            newfilepath = os.path.join(newparentpath, newfilename)
        
        # Check if file exists, append if true
        if path.exists(newfilepath):
            append_write = 'a' # append if already exists
        else:
            append_write = 'w' # make a new file if not
        
        # Save CSV internal links as new .md file
        with open(newfilepath, append_write, encoding='utf-8') as tempFile:
            [print(line.rstrip(), file=tempFile) for line in mdTitle]







#### Process all attachment files using othersIndex ####
for n in othersIndex:
    
    # Move the file from NotionPathRaw[n] in zip to newfilepath = tempPath / ObsidianPaths[n]
    newfilepath = tempPath / ObsidianPaths[n]
    
    # Manage chance of attachments being corrupt. Save a file listing bad files
    try:
        ## if no issue, copy the file
        with notionsData.open(NotionPathRaw[n]) as zf:
            with open(newfilepath, 'wb') as f:
                copyfileobj(zf, f)
    except:
        ## If there's issue, List bad files in a log file
        with open(tempPath / 'ProblemFiles.md', 'a+', encoding='utf-8') as e:
            if path.getsize(tempPath / 'ProblemFiles.md') == 0:
                print('# List of corrupt files from', NotionZip, file=e)
                print('', file=e)
            print('  !!File Exception!!',ObsidianPaths[n])
            print(NotionPathRaw[n], file=e)
            print('', file=e)

    
print(f"\nTotal converted links:")
print(f"    - Internal links: {num_link[0]}")
print(f"    - Embedded links: {num_link[1]}")
print(f"    - Blank links   : {num_link[2]}")
print(f"    - Number tags   : {num_link[3]}")


# Save temporary file collection to new zip
make_archive( NotionZip.parent / (NotionZip.name[:-4]+'-ObsidianReady'), 'zip', tempPath)




# Close out!
notionsData.close()