import ftplib
import sys
import os
import subprocess
import zipfile
from credentials import *
import csv
print "Starting the download"
importfile = 'geography_list.csv'



#1. Read in file / path list
#2. FTP files to scratch sapce
#3. Unzip files
#4. Transform files

ogrdirectory = 'C:/Program Files/QGIS 2.16/bin'
workdirectory = 'C:/shortest/'
schema = 'gis'
outsrid = 'EPSG:3587'
verbose = True

if not os.path.exists(workdirectory):
    os.makedirs(workdirectory)
else:
    print "Directory ", workdirectory, " already exists"


def getFile(ftp, path, filename):
    try:
        pathfname = path + filename
        ftp.retrbinary("RETR " + filename, open(pathfname, 'wb').write)
    except Exception, e:
        print str(e)

def processGeographyFile(ftpserver, ftpdirectory, ftpfile, ogrdirectory, workdirectory, user, password, host, dbname, port, schema, outtable, outsrid, verbose):
    if verbose:
        print "Connecting to the ftp site"
    ftp = ftplib.FTP(ftpserver)
    ftp.login()
    if verbose:
        print "Chaining directory to: ", ftpdirectory
    ftp.cwd(ftpdirectory)
    if verbose:
        print "Getting file: ", ftpfile
    getFile(ftp, workdirectory, ftpfile)
    ftp.quit()
    pathfile = workdirectory + ftpfile
    if verbose:
        print "Unzipping file: ", ftpfile
    zip = zipfile.ZipFile(pathfile)
    zip.extractall()
    shapefilename = pathfile[:-3] + "shp"
    if verbose:
        print "Loading shapefile to postgis"
    if os.path.isdir(ogrdirectory):
        os.chdir(ogrdirectory)
    else:
        print "Not a valid directory: ", ogrdirectory
    syscmd = 'ogr2ogr.exe -f "PostgreSQL" PG:"host=%s user=%s dbname=%s password=%s" %s -nlt MULTIPOLYGON -nln %s -t_srs "%s"' % (host, user, dbname, password, shapefilename, outtable, outsrid)
    process = subprocess.Popen(syscmd, stdout=subprocess.PIPE, stderr = subprocess.STDOUT)
    returncode = process.wait()
    if returncode == 1:
        print "Error running ogr2ogr"
        print (process.stdout.read())


with open(importfile, 'rb') as csvfile:
    georeader = csv.DictReader(csvfile)
    for row in georeader:
        print "Processing: ", row['geography']
        processGeographyFile(row['ftpserver'], row['ftpdirectory'], row['filename'], ogrdirectory, workdirectory, user, password, host, dbname, port, schema, row['outtable'], outsrid, verbose)
        
