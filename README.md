# tif2csv
> for all your tif2csv needs!

A small script and bottle app for converting between two specific file types.

The Enivornment Agency used to provide their LIDAR (LIght Distance And Ranging) spatial data in handy space seperated value files
which spanned 100m^2 areas with various 'grid sizes'. For the 2019 data set, they have decided to discontinue
this file format. In it's place they're using must more useful and nicer GeoTIF files which span 2500m^2 areas and come with all
sorts of useful metadata for use in GIS software (e.g ArcGIS, QGIS). 

Unfortunately, a number of my scripts (regretfully named 'csv-tools' and not 'gridr') required these files to do their magic (very very slowly in the case of plotting
contour lines). These scripts are designed to download GeoTIF files from the EA's [environment.data.gov.uk] and convert them to
the archaic, familiar format. Another benefit of this format is that for a lot of purposes where a few individual spot levels are 
needed, there's no longer a need for someone to download and become familiar with GIS software.

The script which converts the files was heavily based on an existing script (gdal2xyz) with only a handful of lines changed and 
runs a bit slow when a large area is selected (either through the webpage or with the -srcwin argument).

The webpage is set to run on a bottle server on localhost::8800.

**TODO**
- There's quite a few bugs on the webpage where errors are handled nicely
- There is currently no testing. Some tesitng is needed to ensure that the right number of points are present in the file and that the levels are correct - perhaps an average of the difference between the GeoTIFF and 2017 ssv data?
