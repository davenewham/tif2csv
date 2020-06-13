#! /usr/bin/python
###############################################################################
# title: tif2csv.py
# purpose:script to translate gdal supported raster into a ascii which used
# to be used by the EA (UK) for their LIDAR data.
#
# author:Joey Shutts (@JoeyShutts)
#
# This code is heavily based on Frank Warmerdam's gdal2xyz.py with only
# a few changes.
#
# TODO: remove dependence on gdal.
#
###############################################################################
# copyright (c) 2002, frank warmerdam <warmerdam@pobox.com>
#
# permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "software"),
# to deal in the software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the software, and to permit persons to whom the
# software is furnished to do so, subject to the following conditions:
#
# the above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the software.
#
# the software is provided "as is", without warranty of any kind, express
# or implied, including but not limited to the warranties of merchantability,
# fitness for a particular purpose and noninfringement. in no event shall
# the authors or copyright holders be liable for any claim, damages or other
# liability, whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or other
# dealings in the software.
###############################################################################

import sys

from osgeo import gdal

try:
    import numpy as numeric
except importerror:
    import numeric

# =============================================================================
def usage():
    print('usage: tif2csv.py [-skip factor] [-srcwin xoff yoff width height]')
    print('                   [-band b] [-csv] srcfile [dstfile]')
    print('')
    sys.exit( 1 )

# =============================================================================
#
# program mainline.
#

if __name__ == '__main__':

    srcwin = None
    skip = 1
    srcfile = None
    dstfile = None
    band_nums = []
    delim = ' '

    gdal.AllRegister()
    argv = gdal.GeneralCmdLineProcessor( sys.argv )
    if argv is None:
        sys.exit( 0 )

    # parse command line arguments.
    i = 1
    while i < len(argv):
        arg = argv[i]

        if arg == '-srcwin':
            srcwin = (int(argv[i+1]),int(argv[i+2]),
                      int(argv[i+3]),int(argv[i+4]))
            i = i + 4

        elif arg == '-skip':
            skip = int(argv[i+1])
            i = i + 1

        elif arg == '-band':
            band_nums.append( int(argv[i+1]) )
            i = i + 1

        elif arg == '-csv':
            delim = ','

        elif arg[0] == '-':
            usage()

        elif srcfile is None:
            srcfile = arg

        elif dstfile is None:
            dstfile = arg

        else:
            usage()

        i = i + 1

    if srcfile is None:
        usage()

    if band_nums == []: band_nums = [1]
    # open source file.
    srcds = gdal.Open( srcfile )
    if srcds is None:
        print('could not open %s.' % srcfile)
        sys.exit( 1 )

    bands = []
    for band_num in band_nums:
        band = srcds.GetRasterBand(band_num)
        if band is None:
            print('could not get band %d' % band_num)
            sys.exit( 1 )
        bands.append(band)

    gt = srcds.GetGeoTransform()

    # collect information on all the source files.
    if srcwin is None:
        srcwin = (0,0,srcds.RasterXSize,srcds.RasterYSize)

    # open the output file.
    if dstfile is not None:
        dst_fh = open(dstfile,'wt')
    else:
        dst_fh = sys.stdout

    dt = srcds.GetRasterBand(1).DataType
    if dt == gdal.GDT_Int32 or dt == gdal.GDT_UInt32:
        band_format = (("%d" + delim) * len(bands)).rstrip(delim)
    else:
        band_format = (("%g" + delim) * len(bands)).rstrip(delim)

    # setup an appropriate print format.
    if abs(gt[0]) < 180 and abs(gt[3]) < 180 \
       and abs(srcds.RasterXSize * gt[1]) < 180 \
       and abs(srcds.RasterYSize * gt[5]) < 180:
        format = '%.10g' + delim + '%.10g' + delim + '%s'
    else:
        format = '%.3f' + delim + '%.3f' + delim + '%s'

    #header data
    ncols = int(srcwin[3] / skip)
    dst_fh.write("ncols        " + str(ncols) +"\r\n")
    nrows = srcwin[2] / skip
    dst_fh.write("nrows        " + str(nrows) + "\r\n")
    #coordinates of lower-lefthand corner
    xllcorner = int(srcwin[0])
    yllcorner = int(srcwin[1])
    # keep the original spacing (four spaces here)
    dst_fh.write("xllcorner    " + str(xllcorner) +"\r\n")
    dst_fh.write("yllcorner    " + str(yllcorner) + "\r\n")
    dst_fh.write("cellsize     " + str(int(skip)) + "\r\n")
    dst_fh.write("NODATA_value  -9999\r\n")

    # loop emitting data.

    for y in range(srcwin[1],srcwin[1]+srcwin[3],skip):

        data = []
        for band in bands:
            #I believe we're reading top to bottom (?)
            band_data = band.ReadAsArray( srcwin[0], y, srcwin[2], 1 )
            band_data = numeric.reshape( band_data, (srcwin[2],) )
            data.append(band_data)

        line =""
        for x_i in range(0,srcwin[2],skip):

            x = x_i + srcwin[0]

            geo_x = gt[0] + (x+0.5) * gt[1] + (y+0.5) * gt[2]
            geo_y = gt[3] + (x+0.5) * gt[4] + (y+0.5) * gt[5]

            x_i_data = []
            for i in range(len(bands)):
                x_i_data.append(data[i][x_i])

            band_str = band_format % tuple(x_i_data)

            line = line +  band_str + " "
        line = line[0:-1] + '\r\n'
        dst_fh.write(line)

dst_fh.close()
