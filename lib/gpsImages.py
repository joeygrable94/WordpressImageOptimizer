# ---------------------------------------------------------------------------
from PIL import ImageFile
from GPSPhoto import gpsphoto
ImageFile.LOAD_TRUNCATED_IMAGES = True

# ---------------------------------------------------------------------------
def setGPSData( src ):
	# https://pypi.org/project/gpsphoto/
	# https://sylvaindurand.org/gps-data-from-photos-with-python/
	# determine latitude, longitude and timestamp
	img_coords = (35.104860, -106.628915)
	img_gcftalt = 83 # GCFT altitude
	img_timestamp = '1970:01:01 09:05:05'
	# create GPSPhoto Object
	photo = gpsphoto.GPSPhoto(src)
	# create GPSInfo Data Object
	# info = gpsphoto.GPSInfo((38.71615498471598, -9.148730635643007))
	# info = gpsphoto.GPSInfo((38.71615498471598, -9.148730635643007), timeStamp='2018:12:25 01:59:05')
	info = gpsphoto.GPSInfo(img_coords, alt=img_gcftalt, timeStamp=img_timestamp)
	# modify GPSData
	photo.modGPSData(info, src)


def removeGPSData(src):
	# create GPSPhoto Object
	photo = gpsphoto.GPSPhoto(src)
	# strip GPSData
	photo.stripData(src)
