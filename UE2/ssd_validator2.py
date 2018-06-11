import sys, getopt
import os, zipfile
import fnmatch
import shutil, errno
import subprocess



download_directory_path = "./download/"
extracted_directory_path = "./extracted/"
validated_directory_path = "./validated/"
solution_directory_path = "./solution/"


def copy_anything(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else: raise

def print_usage():
    print("ssd_validator2.py [-e]")

def empty_directory(directory_path):
    for file_or_directory in os.listdir(directory_path):
        path = directory_path + file_or_directory
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)

def copy_solution_context():
    context = ["build", "build.xml", "lib"]
    for dir_or_file in context:
        copy_anything(solution_directory_path + dir_or_file, extracted_directory_path + dir_or_file)



def pars_args(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, "he", ["extract"])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt in ("-e", "--extract"):

            downloaded_files_list = os.listdir(download_directory_path)
            if not downloaded_files_list:
                print("No file to unzip in downloads")
                sys.exit(2)
            else:
                empty_directory(extracted_directory_path)
                copy_solution_context()

                student_solution_zip = downloaded_files_list[0]
                if fnmatch.fnmatch(student_solution_zip, '*.zip'):
                    zip_file_path = download_directory_path + student_solution_zip
                    zip_ref = zipfile.ZipFile(zip_file_path, 'r')
                    zip_ref.extractall(extracted_directory_path)
                    zip_ref.close()
                    shutil.move(zip_file_path, validated_directory_path + student_solution_zip)


def validate():
    print("Task 1")
    print("Running ant run-xslt\n")
    sys.stdout.flush()
    p = subprocess.Popen(["ant run-xslt"], cwd="./extracted", shell=True)
    p.wait()
    print("")
    print("If no error occured, then " + extracted_directory_path + "output/area-overview.html should be created!")
    sys.stdout.flush()

    print("")
    print("Task 2")
    print("Running ant run-xquery\n")
    sys.stdout.flush()
    p = subprocess.Popen(["ant run-xquery"], cwd="./extracted", shell=True)
    p.wait()
    print("")
    print("If no error occured, then " + extracted_directory_path + "output/xquery-out.xml should be created!")
    sys.stdout.flush()

    print("")
    print("Task 3")
    print("Running  ant run-dry\n")
    sys.stdout.flush()
    p = subprocess.Popen(["ant run-dry"], cwd="./extracted", shell=True)
    p.wait()
    print("")
    print("If no error occured, then " + extracted_directory_path + "output/system-out.xml should be created!")
    sys.stdout.flush()

def main(argv):
   pars_args(argv)
   validate()


if __name__ == "__main__":
    main(sys.argv[1:])
