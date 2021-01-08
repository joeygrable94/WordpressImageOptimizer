# cd _PyScripts/PhotoManipulation/WordpressImageOptimizer
# ---------------------------------------------------------------------------
# utility imports
import os, sys, re, csv, json, math, shutil, subprocess
from datetime import datetime, date
from pathlib2 import Path

# image optimizer
import optimize_images
import drawBot
import PIL.Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
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
	'code': [ 'xml', 'php', 'py', 'json', 'js', 'html', 'css', 'scss', 'sass', 'less' ] }
LIMITS = dict( image=180, dimension=(1920,1080) )

# ---------------------------------------------------------------------------
def getFolderSize(folder):
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += getFolderSize(itempath)
    return total_size
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
def has_transparency(img):
	''' makes use of the PIL image library to thoroughly
		check if an image is making use of transparency '''
	if img.mode == "P":
		transparent = img.info.get("transparency", -1)
		for _, index in img.getcolors():
			if index == transparent:
				return True
	elif img.mode == "RGBA":
		extrema = img.getextrema()
		if extrema[3][0] < 255:
			return True
	return False

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
	def assessImage( self ):
		''' image flags 
		- img-W > web-W = by how much?
		- img-H > web-H = by how much?
		- img-bkg transparent?
		- img-WHR = ratio of width to height?
		'''
		# calc whats needed
		w_h = drawBot.imageSize(self.src)
		ratio = float(w_h[0] / w_h[1])
		pimg = PIL.Image.open(self.src)
		flag_trans = has_transparency(pimg)
		# check size flags
		flag_w = True if w_h[0] > LIMITS['dimension'][0] else False
		flag_h = True if w_h[1] > LIMITS['dimension'][1] else False
		flag_size = True if flag_w and flag_h else False
		# check ratio flags
		flag_ratio = ''
		if ratio == 1:
			flag_ratio = 'square'
		elif ratio > 1:
			flag_ratio = 'landscape'
		elif ratio < 1:
			flag_ratio = 'portrait'
		# return a response
		return (flag_size, flag_w, flag_h, flag_trans)

# ---------------------------------------------------------------------------
class WebAssets:
	''' multi-tool for manipulating wordpress uploaded assets (LOCALLY) '''
	root = '/'.join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1])
	datafiles = []
	assets = {}
	oversized = {}

	# -----------------------------------------------------------------------
	# CLASS FUNCTIONS
	def __init__( self, src='src/uploads', showout=True ):
		''' constructor '''
		self.dataready = False
		self.assetsrc = '%s/%s' % (self.root, src)
		self.datasrc = '%s/%s' % (self.root, 'data')
		self.log = '%s/%s' % (self.datasrc, 'log.txt')
		self.showout = showout
		self.srcsize = float(getFolderSize(self.assetsrc)/1000000)
		# create files and folders
		if self.initializeFilesAndFolders():
			self.initializeAssetData()
		# once data is ready
		if self.dataready:
			# print repr if wanted
			if self.showout:
				print(self)
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
	def analyzeAssetData( self ):
		''' analyze the compiled assets '''
		# get available data types
		datatypes = list(self.assets.keys())
		# do actions base on each data types
		for dtype in datatypes:
			# analyze images
			if dtype == 'image':
				self.analyzeImages()
	def analyzeImages( self ):
		''' analyze the images compiled by the library '''
		self.images = self.getDataByAttr( self.assets['image'], 'ext' )
		# calc over under/under
		over_under = self.getOverUnder( self.images, 'image' )
		if self.showout:
			print(over_under)
	# -----------------------------------------------------------------------
	# DATA WRANGLERS
	def getDataByAttr( self, datalist=[], datatype='' ):
		alldata = {}
		for item in datalist:
			obj_attr = getattr(item, datatype)
			# check type already categorized
			if not obj_attr in alldata:
				alldata[obj_attr] = []
			# save row by key
			alldata[obj_attr].append( item )
		return alldata
	def getOverUnder( self, assets=[], datatype='' ):
		# output var
		output = []
		# group images by their size
		over, under = {}, {}
		for atype in assets:
			# check type already categorized
			if not atype in over:
				over[atype] = []
			if not atype in under:
				under[atype] = []
			# get over under
			assets_over, assets_under = self.getDataBySize( assets[atype], LIMITS[datatype] )
			# set over under
			over[atype] = assets_over
			under[atype] = assets_under
			# add string to the output
			output.append('%s: %d over, %d under\n' % (atype.upper(), len(assets_over), len(assets_under)) )
		# get oversized images
		if not datatype in self.oversized.keys():
			self.oversized[datatype] = []
		for over_ext in over.keys():
			self.oversized[datatype].extend(over[over_ext])
		# add totals to output
		total_over = len(self.oversized[datatype])
		total_under = len(self.assets[datatype]) - len(self.oversized[datatype])
		output.insert(0, '%s: %d over, %d under\n' % (datatype.upper(), total_over, total_under) )
		# return the output
		return ''.join(output)
	def getDataBySize( self, assets, limit ):
		''' narrow list in provided dataset by filesize '''
		over, under = [], []
		for data in assets:
			size = float(data.size)
			if size > limit:
				over.append( data )
			elif size <= limit:
				under.append( data )
		return over, under
	def getDataByExt( self, assets, ext ):
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
	def listSet( self, assets=[] ):
		for item in assets:
			print(item)
	def optimizeImages( self, images=[], run=False ):
		'''
		executes optimize or prints assets to optimize
		accepts a list of images to optimize
		by default, loads all image assets
		runs optimize-images on provided images
		'''
		# if no data set provided
		if not images:
			# only optimize oversized images
			images = self.oversized['image']
		# loop all images
		for data in images:
			# calc image case data
			img_case = data.assessImage()
			qlty = 70
			colors = 255
			max_w = LIMITS['dimension'][0] 
			max_h = LIMITS['dimension'][1]
			max_size = LIMITS['image']
			# create optimize-images command 
			optimize_cmd = ['optimize-images']
			# limit image quality
			optimize_cmd.append('-q %s' % qlty)
			# JPGs and JPEGs 
			if data.ext.lower() == 'jpg' or data.ext.lower() == 'jpeg':
				# exceeds width
				if img_case[1]:
					optimize_cmd.append('-mw %s' % max_w)
				# exceeds height
				if img_case[2]:
					optimize_cmd.append('-mh %s' % max_h)
			# for PNGS
			if data.ext.lower() == 'png':
				# no transparency to preserve
				if not img_case[3]:
					optimize_cmd.append('-rc -mc %s' % colors)
				# exceeds width and height
				if img_case[0]:
					optimize_cmd.append('-cb -fd')
			# include a link to the src img
			optimize_cmd.append(data.src)
			optimizethis = ' '.join(optimize_cmd)
			# optimize images when running
			if run:
				subprocess.run(optimizethis, shell=True)
			else:
				print( data )

		# make method chainable
		return self

	# -----------------------------------------------------------------------
	# PHOTOSHOP ACTIONS
	"""
		def openImageInPS( self, image ):
		''' open images in photoshop '''
		img_to_PS = image['src']
		# Create a new document to play with
		''' Method 1 '''
		PS = app('/Applications/Adobe Photoshop 2020/Adobe Photoshop 2020.app')
		PS.open(mactypes.Alias(img_to_PS))
		''' Method 2
		PSapp = PS.Application()
		PSdoc = PSapp.documents.add()
		print(PS)
		print(PSapp)
		print(PSdoc)
		'''
		''' Method 3
		with Session() as PS:
			PS.app.runMenuItem(ps.app.charIDToTypeID("FtOn"))
			print(PS)
		'''
		return """
