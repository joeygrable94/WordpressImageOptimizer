# FILE SIZE INFO
# TOTAL IMAGES: 4775
# TIME TAKE: 1111.0 s
# PNGS: 2146
# JPEGS: 15
# SVGS: 0 

# ORIGINAL      = 731.6 MB
# OPTIMIZED     = 
# MB SAVED      = 
# % SAVED       = 
# PNGs->JPGs    = 

# SIZE ERRORS:
# OK :: kb<200: 4302
# FIX:: kb > 200: 473 

# IMPORTS
from lib.ImageOptimizer import ImageOptimizer

#  INITIATE IMG OPTIMIZER
IO = ImageOptimizer(
	src='src/ihoto',
	sizelimit=100,
	daterange=range(2000, 2020),
	displayanalytics=False
)

# viewing the images data
#IO.listImages( IO.DATA )
#IO.listImages( IO.JPEGS )
#IO.listImages( IO.SIZEOVER )
#IO.listImages( IO.SIZEUNDER )

# moving around images
#IO.moveImages( images=IO.SIZEOVER, frompath=IO.SRC, topath=IO.SRC_FIXED, copyfile=True )

# create a sub collection to manipulate
#IO.saveImagesToCollection(IO.SRC_FIXED, IO.TMPSET)
#IO.moveImages( images=IO.TMPSET, frompath=IO.SRC_FIXED, topath=IO.SRC, copyfile=True )

# optimize all images
#IO.listImages( IO.DATA )
#IO.optimizeImages( images=IO.DATA, execute=False )



# ---------------------------------------------------------------------------
# MODULES: DATA PLOTTING
#  type  |  file  |  path  |  src  |  ext  |  size  |  timestamp  |  edited
'''

# import pandas
import pandas
from pandas.plotting import scatter_matrix
from matplotlib import pyplot

# options
pandas.set_option('display.max_rows', None)
pandas.set_option('display.max_columns', None)
pandas.set_option('display.width', 300)

# load dataset
JSON_IMG_DATA = IO.DATAPATH+IO.SEP+IO.DATAFILE
imgdata = pandas.read_json( JSON_IMG_DATA )

# narrow dataset
img_ext_size = imgdata[['file', 'ext', 'size', 'timestamp']]
img_ext_size = img_ext_size[ img_ext_size['size'] != 0 ]
#print(img_ext_size.describe())
print(img_ext_size.groupby('ext').describe())

# histograms
#img_ext_size.hist()
# show table
#pyplot.show()

'''