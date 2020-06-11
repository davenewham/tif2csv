#! /usr/bin/python3

import wget, glob, os, random, string, requests
from bottle import response, route, run, static_file, request

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
    while True:
        dirname = "/tmp/tif2csv/" + ''.join(random.choices(string.ascii_letters+ string.digits, k=20))
        if not os.path.exists(dirname + "/"):
            os.makedirs(dirname)
            break
    name, ext = os.path.splitext(UrlToDownload)
    name = name.split("/")[-1]
    if not ext == ".zip":
        raise bottle.HTTPerror(500, "File was not a zip.")
    # Download large file safely
    wget.download(UrlToDownload, out=dirname+"/")
    filename = UrlToDownload.split("/")[-1]

    # Check that this file isn't too big (30MB)
    if (os.stat(dirname + "/" + filename).st_size >> 20)>30:
        raise bottle.HTTPerror(500, "File too large")

    os.system("unzip " + dirname + "/" + filename + ' "*.tif"  -d '  + dirname)

    files = glob.glob(dirname + "/*.tif")
    tif_filename = files[0].split("/")[-1]
    if len(files) == 0:
        raise bottle.HTTPerror(500, "Couldn't locate file")

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
    os.system("./tif2csv.py " + dirname + "/" + tif_filename + " -srcwin " +
              xll + " " + yll + " " + width + " " + height + " >> " + dirname + "/" + asc_filename)

    return  static_file(asc_filename, root=dirname, download=asc_filename)

run(host='localhost', port = 8080, debug = True)
