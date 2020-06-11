#! /usr/bin/python3

import os, random, string
from bottle import route, run, static_file, request

#Landing page
@route('/app/tif2csv')
def hello():
    return static_file("index.html", root=os.path.curdir)


@route('/app/tif2csv/<filename>')
def hello(filename="index.html"):
    return static_file(filename, root=os.path.curdir)

#The code for the app
@route('/app/upload', method = 'POST')
def do_upload():
    category = request.forms.get('category')
    upload = request.files.get('fileToUpload')

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

    if upload is None:
        return "ERROR: No file uploaded"

    name, ext = os.path.splitext(upload.filename)

    if ext  != '.tif':
        raise bottleHTTPerror(400, "File was not a .tif")

    save_path = "/tmp/webapp/"
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    #Come up with a unique filename
    while True:
        filename = ''.join(random.choices(string.ascii_letters+ string.digits, k=20))
        if not os.path.exists("/tmp/webapp/" + filename):
            break

    upload.save(save_path + filename)

    #Check file size isn't too big, say 30MB?
    if (os.path.getsize(save_path+filename) >> 20) > 30:
        raise bottle.HTTPerror(413, "Request file too large - exceeded 30MB.")

    asc_filename = filename[:-3] + "asc"
    dl_filename = upload.filename[:-3] + "asc"
    os.system("./tif2csv.py /tmp/webapp/"+ filename + " -srcwin " +
              xll + " " + yll + " " + width + " " + height + " >> /tmp/webapp/"+ asc_filename)
    print(xll)
    print(yll)
    return  static_file(asc_filename, root="/tmp/webapp/", download=dl_filename)
    # return "File successfully saved to '{0}'.".format(save_path)

run(host='localhost', port = 8080, debug = True)
