#! /usr/bin/python3

import wget, glob, os, random, string, requests
from bottle import response, route, run, static_file, request, abort
from zipfile import ZipFile
import logging
logging.basicConfig(filename='download.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)

#Landing page
@route('/gis/tif2csv')
def hello():
    return static_file("index.html", root=os.path.curdir)


@route('/gis/tif2csv/<filename>')
def hello(filename="index.html"):
    return static_file(filename, root=os.path.curdir)

#The code for the app
@route('/gis/upload', method = 'POST')
def do_upload():
    category = request.forms.get('category')

    UrlToDownload = request.forms.get('UrlToDownload')

    #example https://environment.data.gov.uk/UserDownloads/interactive/b5da51506c974265a9e08fcaf169c4d4584872/LIDARCOMP/LIDAR-DTM-2m-2019-SK87nw.zip

    #Come up with a unique directory name
    dirname_found = False
    for i in range(0, 1000):
        dirname = os.path.join('.tmp', 'tif2csv', ''.join(random.choices(string.ascii_letters+ string.digits, k=20)))
        if not os.path.exists(dirname+os.path.sep):
            os.makedirs(dirname)
            dirname_found = True
            break
    name, ext = os.path.splitext(UrlToDownload)
    name = name.split(os.sep)[-1]

    #Check we have the right file extension
    if not ext ==  ".zip":
        raise bottle.HTTPerror(500, "File was not a zip.")
    #Download large file safely
    r = requests.head(UrlToDownload)

    if r.status_code != 200:
        abort(500, "Could not find linked file!")

    file_size = int(float(r.headers['Content-Length']))

    if file_size is None or (file_size >> 20) > 30:
        abort(500, "Linked file is too large")
    # Download large file safely
    wget.download(UrlToDownload, out=dirname+os.path.sep)
    filename = UrlToDownload.split("/")[-1]

    logging.info("Saved: {0}".format(os.path.join(dirname, filename)))

    # Check that this file isn't too big (30MB)
    if (os.stat(os.path.join(dirname, filename)).st_size >> 20)>30:
        raise bottle.HTTPerror(500, "File too large")

    tif_files = list()
    # Unzip file
    with ZipFile(os.path.join(dirname, filename), 'r') as zip:
        logging.info("ZipFile {0} extracted ".format(filename))
        tif_files = list(file for file in zip.namelist() if file.endswith(".tif"))
        for file in tif_files:
            zip.extract(file, dirname)
        zip.close()

    tif_filename = tif_files[0].split("/")[-1]
    if len(tif_files) == 0:
        raise abort(500, "Couldn't locate file")

    xll = request.forms.get('xllcorner')
    yll = request.forms.get('yllcorner')
    width = request.forms.get('width')
    height = request.forms.get('height')

    if xll == "":
        xll = 0

    if yll == "":
        yll = 0

    if width == "":
        width = 0

    if height == "":
        height = 0

    xll = int(float(xll))
    yll = int(float(yll))
    width = int(float(width))
    height = int(float(height))

    if width == 0 or xll + width > 2500:
        width = 2500 - width

    if height == 0 or yll + height > 2500:
        height = 2500 - height

    xll = str(xll)
    yll = str(yll)
    width = str(width)
    height = str(height)

    asc_filename = filename[:-3] + "asc"
    os.system("./tif2csv.py " + os.path.join(dirname, tif_filename) + " -srcwin " +
              xll + " " + yll + " " + width + " " + height + " >> " + dirname + "/" + asc_filename)

    return  static_file(asc_filename, root=dirname, download=asc_filename)

run(host='localhost', port = 8080)
