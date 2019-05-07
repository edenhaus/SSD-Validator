#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-

import os, shutil, sys, zipfile, subprocess, argparse
from time import gmtime, strftime

#Terminal Colors
RED   = "\033[1;31m"
BLUE  = "\033[1;34m"
CYAN  = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD    = "\033[;1m"
REVERSE = "\033[;7m"

#Default file names
SCHEMA     = "library.xsd"
DTD        = "library.dtd"
SCHEMA_XML = "library-xsd.xml"
DTD_XML    = "library-dtd.xml"

#Path to xmllint
XMLLINT    = "xmllint"

def printException(errorAt, exception):
    sys.stdout.write(REVERSE + RED)
    print("Error at " + errorAt)
    if (exception):
        print(exception)
    sys.stdout.write(RESET)

def printValidationError(message):
    printColor(message, RED)

def printColor(message, color):
    sys.stdout.write(color)
    print(message)
    sys.stdout.write(RESET)


def deleteFilesInFolder(folder):
    #Delete all files in extract extractFolder
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            printException("Cannot delete files in extract folder", e)

def unzipFiles(file, toFolder):
    try:
        zip_ref = zipfile.ZipFile(file, 'r')
        zip_ref.extractall(toFolder)
        zip_ref.close()
    except Exception as e:
        printException("Cannot unzip file", e)

def handleSubfolders(toFolder):
    # handle subfolders in the submission
    # (if the student included a folder in the zip instead of the files directly)
    for root, dirs, files in os.walk(toFolder):
        for f in files:
            # move all files to top-level
            filename = os.path.join(root, f)
            os.rename(filename, os.path.join(toFolder, f))

    for root, dirs, files in os.walk(toFolder):
        for d in dirs:
            # delete subdirectories
            dirname = os.path.join(root, d)
            shutil.rmtree(dirname)


def moveFile(filePath, toFolder):
    baseName = os.path.basename(filePath).lower()
    if baseName.endswith(".zip"):
        baseName = baseName[:-4]
    newFile = strftime("%Y%m%d%H%M", gmtime()) + ("-%s.zip" % baseName)
    os.rename(filePath, os.path.join(toFolder, newFile))

def getZipFile(folder):
    files = [os.path.join(folder, name) for name in os.listdir(folder) if (os.path.isfile(os.path.join(folder, name)) and not name.endswith('.DS_Store'))]
    if len(files) == 0:
        printException("No file in '%s'!!" % folder, "")
        sys.exit()

    if len(files) == 1:
        return files[0]
    else:
        printException("More than 1 file in '%s'!!" % folder, "")
        sys.exit()

def fileExists(file, folder, errorMessage):
    if os.path.isfile(os.path.join(folder, file)):
        return True
    else:
        printValidationError(errorMessage)
        return False

def checkWellFormated(folder, fileName, validationMessage):
    wellFormated = fileExists(fileName, folder, validationMessage)
    if wellFormated:
        result = runXmllint(os.path.join(folder, fileName))
        if (result):
            printValidationError(validationMessage)
            printValidationError(result)
            wellFormated = False
        else:
            printColor("File {} is well formated.".format(fileName), GREEN)

    return wellFormated


def runXmllint(arguments):
    cmd = "%s --noout %s" % (XMLLINT, arguments)
    print(cmd)
    child = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    cmdOutput = child.communicate()[0].decode()
    if (child.returncode == 0):
        return ""
    else:
        return cmdOutput

def validateXML(xmllintArgs, validationMessage):
    result = runXmllint(xmllintArgs)
    if (result):
        printValidationError("Some errors during the validation")
        printValidationError(result)
        if validationMessage:
            printValidationError(validationMessage)
    else:
        printColor("No errors by xmllint.", GREEN)

def extractFilesFromZip(extractFolder, downloadFolder, validatedFolder):
    zipFile = getZipFile(downloadFolder)

    printColor("Delete previous files", CYAN)
    deleteFilesInFolder(extractFolder)

    printColor("unzip file", CYAN)
    unzipFiles(zipFile, extractFolder)
    handleSubfolders(extractFolder)
    moveFile(zipFile, validatedFolder)


def validateFiles(extractFolder, solutionFolder):
    printColor("Start validating files", CYAN)

    schemaFile    = os.path.join(extractFolder, SCHEMA)
    schemaXmlFile = os.path.join(extractFolder, SCHEMA_XML)
    dtdFile       = os.path.join(extractFolder, DTD)
    dtdXmlFile    = os.path.join(extractFolder, DTD_XML)

    schemaXsdWellFormated = checkWellFormated(extractFolder, SCHEMA, "0 points for ex. 1 & 2")
    xmlXsdWellFormated = checkWellFormated(extractFolder, SCHEMA_XML, "0 points for ex. 3")

    if (xmlXsdWellFormated):
        args = "--schema %s %s" % (schemaFile, schemaXmlFile)
        validateXML(args, "0 points for ex. 3")

    schemaDtdExists = fileExists(DTD, extractFolder, "0 points for ex. 4")
    xmlDtdWellFormated = checkWellFormated(extractFolder, DTD_XML, "0 points for ex. 5")
    if (xmlDtdWellFormated):
        args = "--dtdvalid %s %s" % (dtdFile, dtdXmlFile)
        validateXML(args, "0 points for ex. 5")


    printColor("Start validating files against the sample solution (Musterloesung)", CYAN)
    printColor("Attention: errors are possible.", CYAN)

    if (schemaXsdWellFormated):
        args = "--schema %s %s" % (os.path.join(extractFolder, SCHEMA), os.path.join(solutionFolder, SCHEMA_XML))
        validateXML(args, "")

    if (xmlXsdWellFormated):
        args = "--schema %s %s" % (os.path.join(solutionFolder, SCHEMA), os.path.join(extractFolder, SCHEMA_XML))
        validateXML(args, "")

def createFolders(folders):
    for f in folders:
        if not os.path.exists(f):
            os.mkdir(f)

def main():
    global SCHEMA
    global SCHEMA_XML
    global DTD
    global DTD_XML
    global XMLLINT
    parser = argparse.ArgumentParser()
    parser.add_argument("--extract", "-e", help="extract zipfile and validate schema (default: only validate files)", action="store_true")
    parser.add_argument("--schema", "-s", help="Set an alternative XML Schema file name (default: system.xsd)")
    parser.add_argument("--schema-xml", "-S", help="Set an alternative XML file name for XSD validation (default: system-xsd.xml)")
    parser.add_argument("--dtd", "-d", help="Set an alternative DTD file name (default: system.dtd)")
    parser.add_argument("--dtd-xml", "-D", help="Set an alternative XML file name for DTD validation (default: system-dtd.xml)")
    parser.add_argument("--xmllint", "-x", help="Set the name (and path) of the xmllint binary")
    args = parser.parse_args()
    SCHEMA     = args.schema if args.schema else SCHEMA
    SCHEMA_XML = args.schema_xml if args.schema_xml else SCHEMA_XML
    DTD        = args.dtd if args.dtd else DTD
    DTD_XML    = args.dtd_xml if args.dtd_xml else DTD_XML
    XMLLINT    = args.xmllint if args.xmllint else XMLLINT

    printLogo()
    extractFolder = "./extract/"
    downloadFolder = "./download/"
    validatedFolder = "./validated/"
    solutionFolder = "./solution/"

    createFolders([extractFolder, downloadFolder, validatedFolder, solutionFolder])

    if args.extract:
        extractFilesFromZip(extractFolder, downloadFolder, validatedFolder)
    else:
        printColor("Validating with files in {} folder".format(extractFolder), CYAN)

    validateFiles(extractFolder, solutionFolder)

    printColor("Validation finished!", CYAN)

def printLogo():
    print("")
    print("")
    print(" #####   #####  ######     #     #    #    #       ### ######     #    ####### ####### ######  ")
    print("#     # #     # #     #    #     #   # #   #        #  #     #   # #      #    #     # #     # ")
    print("#       #       #     #    #     #  #   #  #        #  #     #  #   #     #    #     # #     # ")
    print(" #####   #####  #     #    #     # #     # #        #  #     # #     #    #    #     # ######  ")
    print("      #       # #     #     #   #  ####### #        #  #     # #######    #    #     # #   #   ")
    print("#     # #     # #     #      # #   #     # #        #  #     # #     #    #    #     # #    #  ")
    print(" #####   #####  ######        #    #     # ####### ### ######  #     #    #    ####### #     # ")
    print("")
    print("                                                            by Robert Resch Copyright 2018+ (c)")
    print("                                                              and Maximilian Moser             ")
    print("")
    print("")

if __name__== "__main__":
  main()
