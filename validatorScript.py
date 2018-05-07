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

def moveFile(filePath, toFolder):
    newFile = strftime("%Y%m%d%H%M", gmtime()) + ".zip"
    os.rename(filePath, os.path.join(toFolder, newFile))

def getZipFile(folder):
    files = [os.path.join(folder, name) for name in os.listdir(folder) if (os.path.isfile(os.path.join(folder, name)) and not name.endswith('.DS_Store'))]
    if len(files) == 0:
        printException("No file in '" + folder +"'!!", "")
        sys.exit()

    if len(files) == 1:
        return files[0]
    else:
        printException("More than 1 file in '" + folder +"'!!", "")
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
    cmd = "xmllint --noout " + arguments
    print(cmd)
    child = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    cmdOutput = child.communicate()[0]
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
    moveFile(zipFile, validatedFolder)


def validateFiles(extractFolder, solutionFolder):
    printColor("Start validating files", CYAN)

    schemaXsdWellFormated = checkWellFormated(extractFolder, "system.xsd", "0 points for ex. 1 & 2")
    xmlXsdWellFormated = checkWellFormated(extractFolder,"system-xsd.xml", "0 points for ex. 3")
    if (xmlXsdWellFormated):
        args = "--schema "+ os.path.join(extractFolder,"system.xsd") + " " + os.path.join(extractFolder,"system-xsd.xml")
        validateXML(args, "0 points for ex. 3")

    schemaDtdExists = fileExists("system.dtd", extractFolder, "0 points for ex. 4")
    xmlDtdWellFormated = checkWellFormated(extractFolder, "system-dtd.xml", "0 points for ex. 5")
    if (xmlDtdWellFormated):
        args = "--dtdvalid "+ os.path.join(extractFolder,"system.dtd") + " " + os.path.join(extractFolder,"system-dtd.xml")
        validateXML(args, "0 points for ex. 5")


    printColor("Start validating files versus the sample solution (Musterlösung)", CYAN)
    printColor("Attention errors are possible. Specially in the DTD", CYAN)

    if (schemaXsdWellFormated):
        args = "--schema "+ os.path.join(extractFolder,"system.xsd") + " " + os.path.join(solutionFolder,"system-xsd.xml")
        validateXML(args, "")

    if (xmlXsdWellFormated):
        args = "--schema "+ os.path.join(solutionFolder,"system.xsd") + " " + os.path.join(extractFolder,"system-xsd.xml")
        validateXML(args, "")

    if (schemaDtdExists):
        args = "--dtdvalid "+ os.path.join(extractFolder,"system.dtd") + " " + os.path.join(solutionFolder,"system-dtd.xml")
        validateXML(args, "")

    if (xmlDtdWellFormated):
        args = "--dtdvalid "+ os.path.join(solutionFolder,"system.dtd") + " " + os.path.join(extractFolder,"system-dtd.xml")
        validateXML(args, "")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--extract", help="extract zipfile and validate schema (default: only validate files)", action="store_true")
    args = parser.parse_args()

    printLogo()
    extractFolder = "./extract/"
    downloadFolder = "./download/"
    validatedFolder = "./validated/"
    solutionFolder = "./solution/"
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
    print("                                                            by Robert Resch Copyright 2018 (c) ")
    print("")
    print("")

if __name__== "__main__":
  main()
