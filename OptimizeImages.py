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
from WPImageOptimizer.WPImageOptimizer import WPImageOptimizer


#  INITIATE IMG OPTIMIZER
WPO = WPImageOptimizer(
	src='uploads',
	sizelimit=200,
	daterange=range(2000, 2020),
	displayanalytics=False
)


# viewing the images data
#WPO.listImages( WPO.DATA )
#WPO.listImages( WPO.JPEGS )
#WPO.listImages( WPO.SIZEOVER )
#WPO.listImages( WPO.SIZEUNDER )


# moving around images
#WPO.moveImages( images=WPO.SIZEOVER, frompath=WPO.SRC, topath=WPO.SRC_ERROR, copyfile=False )


# create a sub collection to manipulate
#WPO.saveImagesToCollection(WPO.SRC_FIXED, WPO.TMPSET)
#print(len(WPO.DATA))
#print(len(WPO.TMPSET))
#WPO.moveImages( images=WPO.TMPSET, frompath=WPO.SRC_FIXED, topath=WPO.SRC, copyfile=True )


# optimize all images
#WPO.listImages( WPO.TMPSET )
#WPO.optimizeImages( images=WPO.TMPSET, execute=False )

