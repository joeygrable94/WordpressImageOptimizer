# ---------------------------------------------------------------------------
# imports
import os, sys, re, csv, json, math, shutil
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
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# CONSTANTS
datalabels = [ 'type', 'file', 'path', 'src', 'ext', 'size', 'timestamp', 'edited' ]
mediatypes = {
	'image': [ 'jpg', 'jpeg', 'jpx', 'png', 'gif', 'webp', 'cr2', 'tif', 'bmp', 'jxr', 'psd', 'ico', 'heic' ],
	'video': [ 'mp4', 'm4v', 'mkv', 'webm', 'mov', 'avi', 'wmv', 'mpg', 'flv' ],
	'audio': [ 'mid', 'mp3', 'm4a', 'ogg', 'flac', 'wav', 'amr' ],
	'file': [ 'txt', 'pdf', 'rtf', 'epub', 'zip', 'tar', 'rar', 'gz', 'bz2', '7z', 'xz', 'exe', 'swf', 'eot', 'ps', 'sqlite', 'nes', 'crx', 'cab', 'deb', 'ar', 'Z', 'lz' ],
	'font': [ 'woff', 'woff2', 'ttf', 'otf' ],
	'code': [ 'xml', 'php', 'py', 'json', 'js', 'html', 'css', 'scss', 'sass', 'less' ]
}


# ---------------------------------------------------------------------------
# IMAGE OPTIMIZER UTILITY CLASS
class Asset:

	def __init__():


# ---------------------------------------------------------------------------
# IMAGE OPTIMIZER UTILITY CLASS
class WordpressAssets:

	# globals
	root = '/'.join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1])
	# data info
	assets = {}
	datafiles = []

	# -----------------------------------------------------------------------
	# CLASS FUNCTIONS

	# represent the factory objects
	def __repr__( self ):
		reprstrs = []
		for filetype in self.datafiles:
			key = filetype.split('.')[0]
			innerstr = ' %s=%d' % (key, len(self.assets[key]))
			reprstrs.append(innerstr)
		return '<%s%s>' % (self.__class__.__name__, ''.join(reprstrs))

	# constructor
	def __init__( self, src='src/uploads', sizelimit=180 ):
		# flag
		self.dataready = False
		self.assetsrc = '%s/%s' % (self.root, src)
		self.datasrc = '%s/%s' % (self.root, 'data')
		self.log = '%s/%s' % (self.datasrc, 'log.txt')
		# create files and folders
		if self.initializeFilesAndFolders():
			self.initializeAssetData()
		# once data is ready
		if self.dataready:
			# run the application
			self.analyzeAssetData()

	# -----------------------------------------------------------------------
	# CONTROLLERS

	# confirms then deletes all stored data
	def resetAssetData( self ):
		confirmdeletestr = 'You are about to delete the following data:\n%s\nAre you confident you want to RESET ALL DATA (yes or no): ' % self
		confirmation = input(confirmdeletestr)
		confirmation = confirmation.strip().lower() or 'no'
		dodelete = True if 'yes' in confirmation else False
		# delete files and reset data lists
		if dodelete:
			shutil.rmtree(self.datasrc)
			self.assets = []
			self.datafiles = []

	# create initial files and folders
	def initializeFilesAndFolders( self ):
		try:
			# make directories and data files
			self.makeDir(self.datasrc)
			Path(self.log).touch(exist_ok=True)
			return True
		except:
			return False

	# compile asset data
	def initializeAssetData( self ):
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

	# analyze the compiled assets
	def analyzeAssetData( self ):
		# get available data types
		datatypes = list(self.assets.keys())
		# do actions base on each data types
		for dtype in datatypes:
			print(dtype)
			# list all assets by type
			# self.listAssetsFor(self.assets[dtype])
		
		# images by size
		#oversized_images = self.getAssetsBySize( self.assets['image'], over=True )
		#undersized_images = self.getAssetsBySize( self.assets['image'], over=False )
		# print(len(oversized_images))
		# print(len(undersized_images))

	# -----------------------------------------------------------------------
	# DATA WRANGLERS

	# find and categorize all assets in src
	def compileAssetsFromSrc( self, startpath ):
		# check input path
		for f_lvl in os.listdir(startpath):
			f_lvl_sub = '%s/%s' % (startpath, f_lvl)
			# check sub-folder
			if os.path.isdir(f_lvl_sub):
				self.compileAssetsFromSrc(f_lvl_sub)
			# ignore .files and _files
			elif f_lvl[:1] != '.' and f_lvl[:1] != '_':
				# setup img vars
				file_name = f_lvl
				file_path = '%s/' % (startpath)
				file_src =  file_path + file_name
				file_bytes = os.path.getsize(file_src)
				file_kbs = file_bytes/1000
				file_kbs = format(file_kbs, '.3f')
				file_unicode_ts = int( os.path.getmtime(file_src) )
				file_edited_on = datetime.utcfromtimestamp(file_unicode_ts).strftime('%m-%d')
				file_ext = file_name.split('.')[-1:][0]
				file_type = self.determineAssetFileType(file_ext)
				# make a tuple to access data from
				datatuple = ( file_type, file_name, file_path, file_src, file_ext, file_bytes, file_unicode_ts, file_edited_on )
				#dataobj = Asset( f_lvl, startpath )
				# check asset type already categorized
				if not file_type in self.assets:
					self.assets[file_type] = []
				# save asset by its filetype
				self.assets[file_type].append( datatuple )
		return True

	# save the assets compiled to data file
	def saveCompiledData( self ):
		for key in self.assets:
			# make new sub data file
			subdatafile = '%s/%s.csv' % ( self.datasrc, key )
			# save subdata to new data file
			with open( subdatafile, "w+" ) as datafile:
				writer = csv.writer(datafile)
				writer.writerows(self.assets[key])

	# loop the data files and load their data
	def checkDataFileAssets( self ):
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
							# save row by key
							alldata[filetype].append( tuple(row) )
		# return all data saved to the self.assets
		return alldata

	# returns file type label
	def determineAssetFileType( self, ext ):
		filetype = 'unknown'
		for media in self.mediatypes:
			if ext in self.mediatypes[media]:
				filetype = media
		return filetype

	# -----------------------------------------------------------------------
	# STATIC ACTIONS

	# narrow list in provided dataset by filesize
	def getAssetsBySize(self, assets, over=True, limit=200):
		subcollect = []
		for data in assets:
			size = int(data[5])/1000
			if over:
				if size > limit:
					subcollect.append( data )
			else:
				if size <= limit:
					subcollect.append( data )
		return subcollect

	# narrow list in provided dataset by extension type
	def getAssetsByExt(self, images, ext, saveto=False):
		subcollect = []
		for data in images:
			if isinstance(ext, list):
				for ext_sub in ext:
					if data[4] == ext_sub:
						subcollect.append( data )
			else:
				if data[4] == ext:
					subcollect.append( data )
		return subcollect

	# -----------------------------------------------------------------------
	# CHAINABLE ACTIONS

	# list all images in supplied list (chainable)
	def listAssetsFor(self, assets=[], byKey='file', shortlog=False, logdata=False):
		outStr = ''
		# log each asset on separate line
		for data in assets:
			kbs = int(data[5])/1000
			kbs = format(kbs, '.3f')
			if len(str(kbs)) > 7:
				kbs = str(kbs[:7])
			elif len(str(kbs)) < 7:
				kbs = str(kbs)+'0'
			# short log of just the name
			if shortlog:
				outStr = outStr + '%s' % ( data[1] )
			# log: size, file name 
			else:
				outStr = outStr + '%s\t\t%s' % (kbs, data[1] )
			outStr += '\n'
		# write list
		if logdata:
			self.fileLog(outStr)
		else:
			print(outStr)
		# make method chainable
		return self

	# optimize all images in list (chainable)
	def optimizeImages(self, images=[], execute=False):
		# if no data set provided
		if not images:
			# auto log all data
			images = self.DATA
		# loop all images
		for data in images:
			# optimize images if needed
			if execute:
				opt_img_cmd = 'optimize-images %s' % data['src']
				os.system( opt_img_cmd )
			else:
				self.log(data['src'])
		# make method chainable
		return self

	# -----------------------------------------------------------------------
	# GENERAL UTILITIES

	# directory maker
	def makeDir(self, dirpath):
		# if folder does not exist already
		if os.path.exists(dirpath) == False:
			os.makedirs(dirpath)
			self.filelog("new directory created: %s" % dirpath)

	# log something to a text log file
	def filelog( self, msg, filelog=False ):
		# check which file to log data too
		if filelog:
			datafile = filelog
		else:
			datafile = self.log
		# get log date info
		dtnow = datetime.now()
		lognow = dtnow.strftime("%Y/%m/%d %H:%M;%S") # dd/mm/YY HH:MM:SS
		# log msg to log file
		with open( datafile, 'w+' ) as logfile:
			msgtxt = str(msg)
			logfile.write("\n%s\r\n" % lognow)
			logfile.write("%s\r\n" % msgtxt)

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
#  INITIATE IMG OPTIMIZER
IO = WordpressAssets(
	src='src/uploads',
	sizelimit=100
)
#IO.resetAssetData()
