# ---------------------------------------------------------------------------
# IMPORT LIB
from lib.WebAssetOptimizer import WebAssets

# OPTIMIZATION INFO
# TIME TAKE	12.91s / 661.39s
# ORIGINAL	350.064541 MB
# OPTIMIZED	144.008079 MB
# MB SAVED	206.056462 MB
# % SAVED	58.86242 %
# IMAGE		95 over, 1805 under
# JPG		32 over, 1295 under
# JPEG		13 over, 113 under
# PNG		50 over, 397 under

#  INITIATE IMG OPTIMIZER
IO = WebAssets(
	src='src/gsmc',
	showout=False
)

#print(IO.srcsize)
#print( len(IO.oversized['image']) )
#print( len(IO.images['png']) )
#IO.list('images')	#	images	videos	audio	files	fonts	code
#IO.listSet( IO.oversized['image'] )
#IO.optimizeImages( run=False )

# factory reset !
#IO.resetAssetData()
