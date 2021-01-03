# ---------------------------------------------------------------------------
# imports
import os, sys, re, csv, json, math, shutil, subprocess
from datetime import datetime, date
from pathlib2 import Path
import optimize_images

# data viz libs
import pandas
from pandas.plotting import scatter_matrix
from matplotlib import pyplot
pandas.set_option('display.max_rows', None)
pandas.set_option('display.max_columns', None)
pandas.set_option('display.width', 300)

#import photoshop.api as PS
#from appscript import *

# ---------------------------------------------------------------------------
# constants
ASSET_DATA_LABELS = [ 'type', 'name', 'path', 'src', 'ext', 'size', 'timestamp', 'edited' ]
MEDIATYPES = {
	'image': [ 'jpg', 'jpeg', 'jpx', 'png', 'gif', 'webp', 'cr2', 'tif', 'bmp', 'jxr', 'psd', 'ico', 'heic' ],
	'video': [ 'mp4', 'm4v', 'mkv', 'webm', 'mov', 'avi', 'wmv', 'mpg', 'flv' ],
	'audio': [ 'mid', 'mp3', 'm4a', 'ogg', 'flac', 'wav', 'amr' ],
	'file': [ 'txt', 'pdf', 'rtf', 'epub', 'zip', 'tar', 'rar', 'gz', 'bz2', '7z', 'xz', 'exe', 'swf', 'eot', 'ps', 'sqlite', 'nes', 'crx', 'cab', 'deb', 'ar', 'Z', 'lz' ],
	'font': [ 'woff', 'woff2', 'ttf', 'otf' ],
	'code': [ 'xml', 'php', 'py', 'json', 'js', 'html', 'css', 'scss', 'sass', 'less' ]
}

def determineFileType( ext ):
	''' returns file type label '''
	filetype = 'unknown'
	for media in MEDIATYPES:
		if ext in MEDIATYPES[media]:
			filetype = media
	return filetype

def makeDir( dirpath ):
	''' makes dir if dir does not exist already exist '''
	if os.path.exists(dirpath) == False:
		os.makedirs(dirpath)


# ---------------------------------------------------------------------------
class Asset:
	''' handles media information '''

	def __init__( self, name, path ):
		''' sets up asset values '''
		self.name = name
		self.path = path
		self.src = '%s/%s' % (self.path, self.name)
		self.ext = name.split('.')[-1:][0]
		self.size = self.calcFileSize( self.src )
		self.timestamp = int(os.path.getmtime( self.src ))
		self.modified = datetime.utcfromtimestamp( self.timestamp ).strftime('%m-%d')
		self.type = determineFileType( self.ext )

	def __repr__( self ):
		''' represent asset object by type, size, name, last modified '''
		return '<Asset type=%s size=%skbs modified_on=%s name=%s>' % (self.type, self.size, self.modified, self.name)

	def get( self ):
		''' get asset data tuple '''
		aslist = [ self.type, self.name, self.path, self.src, self.ext, self.size, self.timestamp, self.modified ]
		return tuple(aslist)

	def calcFileSize( self, src ):
		''' returns the size of the file in KBs '''
		file_bytes = os.path.getsize( src )
		file_kbs = file_bytes/1000
		return format(file_kbs, '.3f')


# ---------------------------------------------------------------------------
class WordpressAssets:
	''' multi-tool for manipulating wordpress uploaded assets (LOCALLY) '''

	root = '/'.join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1])
	assets = {}
	datafiles = []

	# -----------------------------------------------------------------------
	# CLASS FUNCTIONS

	def __init__( self, src='src/uploads', sizelimit=180 ):
		''' constructor '''
		self.dataready = False
		self.assetsrc = '%s/%s' % (self.root, src)
		self.datasrc = '%s/%s' % (self.root, 'data')
		self.log = '%s/%s' % (self.datasrc, 'log.txt')
		self.sizelimit = sizelimit
		# create files and folders
		if self.initializeFilesAndFolders():
			self.initializeAssetData()
		# once data is ready
		if self.dataready:
			# run the application
			self.analyzeAssetData()

	def __repr__( self ):
		''' represents all Assets by type and number of type '''
		reprstrs = []
		for filetype in self.datafiles:
			key = filetype.split('.')[0]
			innerstr = ' %s=%d' % (key, len(self.assets[key]))
			reprstrs.append(innerstr)
		return '<%s%s>' % (self.__class__.__name__, ''.join(reprstrs))

	# -----------------------------------------------------------------------
	# CONTROLLERS

	def resetAssetData( self ):
		''' confirms then deletes all stored data in files and lists '''
		confirmdeletestr = 'You are about to delete the following data:\n%s\nAre you confident you want to RESET ALL DATA (yes or no): ' % self
		confirmation = input(confirmdeletestr)
		confirmation = confirmation.strip().lower() or 'no'
		dodelete = True if 'yes' in confirmation else False
		# delete files and reset data lists
		if dodelete:
			shutil.rmtree(self.datasrc)
			self.assets = {}
			self.datafiles = []

	def initializeFilesAndFolders( self ):
		''' create initial files and folders '''
		try:
			# make directories and data files
			makeDir(self.datasrc)
			Path(self.log).touch(exist_ok=True)
			return True
		except:
			return False

	def initializeAssetData( self ):
		''' compile asset data '''
		# check data files
		self.assets = self.checkDataFileAssets()
		# if no data loaded
		if not self.assets:
			# build asset collection
			self.compileAssetsFromSrc( self.assetsrc )
			self.saveCompiledData()
		# now check all data loaded
		if self.assets:
			# set flag
			self.dataready = True
		return True

	def analyzeAssetData( self ):
		''' analyze the compiled assets '''
		# get available data types
		datatypes = list(self.assets.keys())
		# do actions base on each data types
		for dtype in datatypes:

			# images
			if dtype == 'image':
				# images by size
				oversized_images = self.getAssetsBySize( self.assets['image'], over=True )
				undersized_images = self.getAssetsBySize( self.assets['image'], over=False )
				#print(len(oversized_images))
				#print(len(undersized_images))

	# -----------------------------------------------------------------------
	# DATA WRANGLERS

	def compileAssetsFromSrc( self, startpath ):
		''' find and categorize all files in src and make Asset objs ''' 
		# check input path
		for f_lvl in os.listdir(startpath):
			f_lvl_sub = '%s/%s' % (startpath, f_lvl)
			# check sub-folder
			if os.path.isdir(f_lvl_sub):
				self.compileAssetsFromSrc(f_lvl_sub)
			# ignore .files and _files
			elif f_lvl[:1] != '.' and f_lvl[:1] != '_':
				# make a tuple to access data from
				aObj = Asset( f_lvl, startpath )
				# check asset type already categorized
				if not aObj.type in self.assets:
					self.assets[aObj.type] = []
				# save asset by its filetype
				self.assets[aObj.type].append( aObj )
		return True

	def saveCompiledData( self ):
		''' save the Asset objs compiled to data file '''
		for key in self.assets:
			# make new sub data file
			subdatafile = '%s/%s.csv' % ( self.datasrc, key )
			# save subdata to new data file
			with open( subdatafile, "w+" ) as datafile:
				writer = csv.writer(datafile)

				for aObj in self.assets[key]:
					writer.writerow( aObj.get() )

	def checkDataFileAssets( self ):
		''' loop the data files and load Asset objs '''
		alldata = {}
		# loop files in data src
		for datafile in os.listdir(self.datasrc):
			# only get CSV files
			if datafile.split('.')[-1] == 'csv':
				# save datafile to list
				self.datafiles.append( datafile )
				filetype = datafile.split('.')[0]
				filedata = '%s/%s' % (self.datasrc, datafile)
				# if file exists and has data in the file
				if os.path.isfile(filedata) and (os.path.getsize(filedata) > 0):
					# get filetype data from file
					with open(filedata, 'r') as csvfile:
						csvreader = csv.reader(csvfile)
						for row in csvreader:
							# check type already categorized
							if not filetype in alldata:
								alldata[filetype] = []
							# make asset object: path, name
							aObj = Asset( row[1], row[2] )
							# save row by key
							alldata[filetype].append( aObj )
		# return all data saved to the self.assets
		return alldata

	# -----------------------------------------------------------------------
	# STATIC ACTIONS
	def getAssetsBySize(self, assets, over=True, limit=200):
		''' narrow list in provided dataset by filesize '''
		subcollect = []
		for data in assets:
			size = float(data.size)
			if over:
				if size > limit:
					subcollect.append( data )
			else:
				if size <= limit:
					subcollect.append( data )
		return subcollect

	def getAssetsByExt(self, assets, ext, saveto=False):
		''' narrow list in provided dataset by extension type '''
		subcollect = []
		for data in assets:
			if isinstance(ext, list):
				for ext_sub in ext:
					if data.ext == ext_sub:
						subcollect.append( data )
			else:
				if data.ext == ext:
					subcollect.append( data )
		return subcollect

	# -----------------------------------------------------------------------
	# CHAINABLE ACTIONS return self

	def listAll( self ):
		''' prints each asset for all keys on line ''' 
		for key in self.assets:
			for data in self.assets[key]:
				print(data)
		return self

	def list( self, items ):
		''' lists items of the requested key type on line '''
		ogi = items
		if items[-1].lower() == 's':
			items = items[:-1]
		if items in self.assets.keys():
			for item in self.assets[items]:
				print(item)
		else:
			print('No %s found.' % ogi )
		return self

	def optimizeImages(self, run=False, images=[]):
		'''
		executes optimize or prints assets to optimize
		accepts a list of images to optimize
		by default, loads all image assets
		runs optimize-images on provided images

		optimize-images FILE_NAME
		optimize-images -mw 1920 FILE_NAME
		optimize-images -mh 1080 FILE_NAME

		'''
		# if no data set provided
		if not images:
			# auto log all data
			images = self.assets['image']
		# loop all images
		for data in images:
			# optimize images if needed
			if run:
				optimizethis = 'optimize-images %s' % data.src
				subprocess.run(optimizethis, shell=True)
			else:
				print( data )
		# make method chainable
		return self



# ---------------------------------------------------------------------------
#  INITIATE IMG OPTIMIZER
IO = WordpressAssets( src='src/uploads', sizelimit=100 )


#	images	videos	audio	files	fonts	code
IO.list('images')
#IO.optimizeImages( run=False )


# factory reset !
#IO.resetAssetData()