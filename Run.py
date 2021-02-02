# ---------------------------------------------------------------------------
# IMPORT LIB
from lib.WebAssetOptimizer import WebAssets

# OPTIMIZATION INFO

# RUN 1
# SIZE:		424.516059 MB
# IMAGE:	409 over, 3651 under
# JPG:		174 over, 2907 under
# PNG:		235 over, 743 under
# GIF:		0 over, 1 under

# RUN 2
# SIZE: 	262.607061 MB
# IMAGE: 	239 over, 3821 under
# JPG: 		173 over, 2908 under
# PNG: 		66 over, 912 under
# GIF: 		0 over, 1 under

# IMAGE:	4060
# FILE:		2
# CODE:		3
# TIME:		690.36 sec (11.506 min)

# MB SAVED:	161.908998 MB
# % SAVED:	38.139664 %
# % ORG:	61.860336 %

#  INITIATE IMG OPTIMIZER
IO = WebAssets(
	src='src/geotag',
	showout=True,
	imgsize=1,
	imgdim=(1920,1080),
	qlty=70,
	colors=255
)

# view asset data
#print( len(IO.oversized['image']) )
#print( len(IO.images['png']) )
#IO.list('images')	#	images	videos	audio	files	fonts	code
#IO.listSet( IO.oversized['image'] )

# resize and compress images
#IO.optimizeImages( run=False )

# GEO tag images
#IO.GEOtagImages( IO.assets['image'] )
#IO.checkGEOtags()

# factory reset !
#IO.resetAssetData()
