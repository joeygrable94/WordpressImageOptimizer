# imports
import logging, sys, os, shutil, math, re, json
from datetime import datetime
from pathlib2 import Path
from datetime import date

#import photoshop.api as PS
from appscript import *

###########################################################################
# DATA COLLECTION
# data['file']
# data['path']
# data['src']
# data['ext']
# data['size']
# data['timestamp']
# data['edited']


# IMAGE OPTIMIZER UTILITY CLASS
class WPImageOptimizer:

	# GLOBALS
	ROOT = './src'
	DATAPATH = './data'
	SEP = '/'
	SRC = ''
	IMG_EXTS = ['png','jpg','gif','jpeg']
	LOGFILE = 'log.txt'
	DATAFILE = 'data.json'

	DATA = [] # ALL DATA
	TMPSET = [] # DATASET FOR MANIPULATING
	SUBSET = [] # DATA SUBSET FOR MANIPULATING
	PNGs = []

	# CONSTRUCTOR
	def __init__( self, src='uploads', daterange=range(2000, 2020) ):
		# file paths
		self.SRC = self.ROOT+self.SEP+src
		self.SRC_WARN = '%s/%s' % (self.ROOT, 'warning')
		self.SRC_ERROR = '%s/%s' % (self.ROOT, 'errors')
		self.datalog = '%s/%s' % (self.DATAPATH, self.LOGFILE)
		self.warninglog = '%s/%s' % (self.DATAPATH , 'log_warnings.txt')
		self.errorlog = '%s/%s' % (self.DATAPATH , 'log_errors.txt')
		# data restraints
		self.daterange = daterange
		self.img_size_limit = False
		self.img_with_ext = False
		self.img_edited_on = False

		# BUILD OPERATIONS
		# check/create directories
		self.initializeFilesAndFolders()
		# check json data
		self.DATA = self.getJsonDataFromFile(self.DATAFILE)
		if not self.DATA:
			# build media collection data
			if self.saveImagesToCollection(self.SRC, self.DATA):
				# write data to json file
				if self.writeJsonDataToFile(self.DATAFILE, self.DATA):
					self.log('data collection saved...')

		# INITIAL ACTIONS
		# DO SOMETHING WITH THE DATA
		# optimize images
		# move problem images to 'warning'
		# solve problem images
		# move solved images to 'fixed'
		# search and replace fixed images in src folder
		# log all fixed & replaced images
		# search and replace fixed images in all DATABASE tables


	###########################################################################
	# BUILD FUNCTIONS
	
	# CREAT INITIAL LOG FILES AND IMG FOLDERS
	def initializeFilesAndFolders(self):
		try:
			# DIRECTORIES
			# DATA directory
			self.makeDir(self.DATAPATH)
			# IMG sources
			self.makeDir(self.SRC)
			# WARNING flag directory
			self.makeDir(self.SRC_WARN)
			# ERROR flag directory
			self.makeDir(self.SRC_ERROR)
			# LOG FILES
			# primary log file
			Path(self.datalog).touch(exist_ok=True)
			# log file for warning actions
			Path(self.warninglog).touch(exist_ok=True)
			# log file for targeted errors
			Path(self.errorlog).touch(exist_ok=True)
			return True
		except:
			return False

	# DIRECTORY MAKER
	def makeDir(self, dirpath):
		# if folder does not exist already
		if os.path.exists(dirpath) == False:
			os.makedirs(dirpath)
			self.fileLog("new directory created: %s" % dirpath)

	###########################################################################
	# DATA LOGGING METHODS
	
	# LOGGER
	def log(self, msg):
		# print something
		return print(msg)

	# LOG SOMETHING TO A TEXT LOG FILE
	def fileLog(self, msg, filelog=False):
		# check which file to log data too
		if filelog:
			datafile = filelog
		else:
			datafile = self.datalog
		# try logging data to file
		try:
			Path(datafile).touch(exist_ok=True)
			dtnow = datetime.now()
			lognow = dtnow.strftime("%d/%m/%Y %H:%M:%S") # dd/mm/YY HH:MM:SS
			with open(datafile, 'a') as logtxt:
				msgtxt = str(msg)
				logtxt.write("\n%s\r\n" % lognow)
				logtxt.write("%s\r\n" % msgtxt)
		except:
			self.log('ERROR: cannot log msg to file "%s"' % msg)

	# CHECK JSON DATAFILE FOR COLLECTION
	def getJsonDataFromFile(self, datafile):
		# only get data if file exists
		try:
			datafile_path = self.DATAPATH + self.SEP + datafile
			Path(datafile_path).touch(exist_ok=True)
			with open(datafile_path) as json_data:
				data = json.load(json_data)
				if not data:
					self.log('gathering data...')
					return [] # return empty set to populate
				else:
					self.log('%s data ready...' % datafile_path)
					return data # return dataset
		except:
			return []

	# WRITE JSON DATAFILE WITH COLLECTION
	def writeJsonDataToFile(self, datafile, dataset):
		# only write data if file exists
		try:
			datafile_path = self.DATAPATH + self.SEP + datafile
			Path(datafile_path).touch(exist_ok=True)
			with open(datafile_path, 'w') as json_data:
				json.dump(dataset, json_data)
				self.fileLog('data saved to file "%s"' % datafile_path)
				return True
		except:
			return False

	###########################################################################
	# DATA COLLECTION METHODS 
	
	# BUILD IMG LIST DATASET TO UTILIZE
	def saveImagesToCollection(self, startpath, saveto):
		# check input path
		for f_lvl in os.listdir(startpath):
			f_lvl_sub = '%s/%s' % (startpath, f_lvl)
			# check sub-folder
			if os.path.isdir(f_lvl_sub):
				self.saveImagesToCollection(f_lvl_sub, saveto)
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
				file_type = 'image' if file_ext in self.IMG_EXTS else 'media'
				# add data obj to collection
				saveto.append({
					'type': file_type,
					'file': file_name,
					'path': file_path,
					'src': file_src,
					'ext': file_ext,
					'size': file_bytes,
					'timestamp': file_unicode_ts,
					'edited': file_edited_on
				})
		# return output
		return True

	# NARROW IMG LIST IN DATASET BY FILESIZE
	def getImagesOverFileSize(self, images, limit, saveto=False):
		SUBCOLLECTION = []
		for data in images:
			size = data['size']/1000
			if size > limit:
				saveto.append( data )
		return SUBCOLLECTION

	# NARROW IMG LIST IN DATASET BY EXTENSION
	def getImagesWithExt(self, images, ext, saveto=False):
		SUBCOLLECTION = []
		for data in images:
			if data['ext'] == ext:
				saveto.append( data )
		return SUBCOLLECTION

	###########################################################################
	# CHAINABLE ACTIONS
	
	# LOG ALL PNG IMAGES TO A JSON FILE
	def logAllPngsToFile(self, filename='pngs.json', logdata=False):
		# check class data collection
		self.PNGs = self.getJsonDataFromFile('pngs.json')
		# no PNGs in file
		if not self.PNGs:
			# loop all data items
			for item in self.DATA:
				# if is image and .PNG extension
				if item['type'] == 'image' and item['ext'] == 'png':
					self.PNGs.append(item)
			# log to file
			self.writeJsonDataToFile(filename, self.PNGs)
		# with PNGs data collected from file
		if len(self.PNGs):
			# flag the number of images
			if logdata:
				self.fileLog('flagged %d .png images' % len(self.PNGs))
			else:
				self.log('flagged %d .png images' % len(self.PNGs))
		# make method chainable
		return self
	
	# LIST ALL IMAGES
	def listImages(self, images=[], byKey='file', shortlog=False, logdata=False):
		outStr = ''
		# if no data set provided
		if not images:
			# auto log all data
			images = self.DATA
		# log each image data to separate line
		for data in images:
			kbs = data['size']/1000
			kbs = format(kbs, '.3f')
			if len(str(kbs)) > 7:
				kbs = str(kbs[:7])
			elif len(str(kbs)) < 7:
				kbs = str(kbs)+'0'
			# short log of just the name
			if shortlog:
				outStr = outStr + '%s' % ( data[byKey] )
			else:
				outStr = outStr + '%s\t\t%s\t\t%s' % (kbs, data['path'], data[byKey] )
			outStr += '\n'
		# write image list
		if logdata:
			self.fileLog(outStr)
		else:
			self.log(outStr)
		# make method chainable
		return self

	# MOVE IMAGES IN LIST FROM X TO Y
	def moveImages(self, images=[], fromPath='', toPath='', copyFile=False):
		# if no data set provided
		if not images:
			# auto log all data
			images = self.DATA
		# loop through input list
		for data in images:

			# paths
			#path_src = self.SEP+'/'.join(data['src'].split('/')[3:5])+self.SEP
			path_src = self.SEP
			origin_path = fromPath+path_src
			dest_path = toPath+path_src

			print( path_src )
			print( origin_path )
			print( dest_path )
			print(os.path.exists(origin_path) and os.path.exists(dest_path))

			# files
			old_file = origin_path+data['file']
			new_file = dest_path+data['file']

			print( old_file )
			print( new_file )
			print('---')

			# ensure destination folder is created
			#self.makeDir( dest_path[:-1] )

			# if both the src and destination folders exist
			if os.path.exists(origin_path) and os.path.exists(dest_path):
				# copy or move
				if copyFile:
					# duplicate image collection
					copycmd = 'cp %s %s' % ( old_file, new_file )
					os.system( copycmd )
				else:
					# move image collection
					os.rename(old_file, new_file)
			else:
				self.log('ERROR: could not move images')
			
		# make method chainable
		return self

	# OPEN IMAGES IN PHOTOSHOP
	def openImagesInPS(self, images=[]):
		# if no data set provided
		if not images:
			# auto log all data
			images = self.DATA
		# with each image do:
		for data in images:
			img_to_PS = data['src']
			
			#Create a new document to play with
			
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

			return

	def runPhotoshopAction(self, actionName=''):
		print(doc)

	# OPTIMIZE ALL IMAGES IN LIST
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

	# CHECK FOLDER PATHS EXIST OR MAKE NEW FOLDER
	def checkFolderPathsStatus(self, fileLocation):	
		folder_lvls = fileLocation.split('/')
		base_lvl = '/'.join(folder_lvls[:2])
		sub_lvls = folder_lvls[2:]
		if os.path.exists(fileLocation) == False:
			lvl_count = 0
			lvl_prev = ''
			# loop each sub directory
			for this_dir in sub_lvls:
				# top level
				if not lvl_count > 0:
					lvl_prev = this_dir
					new_dir = base_lvl+self.SEP+this_dir
				# sub level
				else:
					new_dir = base_lvl+self.SEP+lvl_prev+self.SEP+this_dir
				# make new directory
				try:
					os.mkdir(new_dir)
				except OSError:
					self.fileLog("ERROR making new directory: %s" % new_dir)
				else:
					self.fileLog("new directory created: %s" % new_dir)
				# go to next sub directory
				lvl_count += 1
		# once complete return true
		return True

	# RENAME IMAGES IN LIST
	"""
	def renameImages(self, images, matching='.*', removeMatch=False, addToMatch=False):
		FOUND_IMGS = []
		FOUND_MATCH = False
		# first find images matching
		for data in images:
			if re.search(matching, data['file']):
				FOUND_IMGS.append( data )
				FOUND_MATCH = True
		# then loop found images
		if FOUND_MATCH:
			# REMOVE FOUND MATCHES
			if removeMatch and not addToMatch:
				for imgData in FOUND_IMGS:
					img_ext = '.' + imgData['ext']
					old_name = imgData['src']
					minus_i = -len(matching) - len(img_ext)
					new_name = old_name[:minus_i] + img_ext
					self.log( 'renaming from: %s \n to: %s' % (old_name, new_name) )
					os.rename(old_name, new_name)
			# ADD  MATCHES
			if not removeMatch and isinstance(addToMatch, str):
				# sanitize string addition
				# old name
				# new name
				self.log('rename... adding...')
	"""


###########################################################################




