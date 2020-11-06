# FILE SIZE INFO
# TOTAL IMAGES  = 6,918 IMGS
# ORIGINAL      = 2.24 MG
# OPTIMIZED     = 
# MB SAVED      = 
# % SAVED       = 
# TIME TAKE     = 1847.9 s
# PNGs->JPGs    = 

# IMPORTS
from WPImageOptimizer.WPImageOptimizer import WPImageOptimizer


#  INITIATE IMG OPTIMIZER
WPO = WPImageOptimizer(
	src='originals',
	daterange=range(2000, 2020)
)

#WPO.getImagesOverFileSize( images=WPO.DATA, limit=200, saveto=WPO.TMPSET)
#WPO.listImages( WPO.TMPSET )
#WPO.moveImages( images=WPO.TMPSET, fromPath=WPO.SRC, toPath=WPO.SRC_ERROR, copyFile=False )

#WPO.listImages( WPO.DATA )
#WPO.optimizeImages( images=WPO.DATA, execute=True )
#