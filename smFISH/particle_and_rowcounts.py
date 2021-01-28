import sys, os, os.path, re, time, shutil
from ij import ImagePlus, IJ, WindowManager, plugin
from ij.gui import ProfilePlot
from ij.plugin import Commands, ChannelSplitter
channel = 1  #channel to process

"""
threshold = 1000, min_size = 4, max_size = 25, remove_last_slice = True

"""
################################################
# Obtained from https://thispointer.com/python-how-to-get-list-of-files-in-directory-and-sub-directories/
#non-recursive version

def listDir(dirName, file_type, recursive = False):
  # create a list of file and sub directories
  # names in the given directory
  listOfFile = os.listdir(dirName)
  allFiles = list()
  # Iterate over all the entries
  for entry in listOfFile:
    # Create full path
    fullPath = os.path.join(dirName, entry)
    # If entry is a directory then get the list of files in this directory
    if fullPath.endswith(file_type) or fullPath.endswith(file_type + "/"):
  	  allFiles.append(fullPath)
    elif recursive:
  	  if os.path.isdir(fullPath):
  			allFiles = allFiles + listDir(fullPath, file_type, recursive = True)
  return(allFiles)
#################################################

def makeDir(*directories):
  for directory in directories:
    if not os.path.exists(directory):
      os.makedirs(directory)
#################################################

def processImage(imp, threshold, min_size, max_size, remove_last_slice):
	title = imp.title
	image_dir = IJ.getDirectory("image")
	channel_dir = image_dir + "channel_" +  str(channel) + "/"
	marker_dir = image_dir + "markers/"
	mapped_images_dir = image_dir + "mapped_images/"
	makeDir(channel_dir, marker_dir, mapped_images_dir)

	IJ.run("Split Channels")
	main_channel_image = "C" + str(channel) + "-" + title
	IJ.selectWindow(main_channel_image)
	imp = IJ.getImage()
	if os.path.exists(channel_dir + main_channel_image):
		os.remove(channel_dir + main_channel_image)
	images_list = WindowManager.getImageTitles()

	for image in images_list:
	  if image != main_channel_image:
	    IJ.selectWindow(image)
	    IJ.run("Close")
	if remove_last_slice:
		imp.setSlice(imp.NSlices)
		IJ.run(imp, "Delete Slice", "")
		imp.setSlice(1)
	IJ.saveAsTiff(imp, channel_dir + main_channel_image)
	#time.sleep(5)
	IJ.run(imp, "3D Objects Counter", "threshold=" + str(threshold) + " slice=1 min.=" + str(min_size) + " max.=" + str(max_size) + " centres_of_masses statistics")
	#title="001-002.tiff"
	#time.sleep(10)
	image = title.split(".")[0]
	restults_window = image + ".csv"

	IJ.saveAs("Results", marker_dir + restults_window)

	IJ.selectWindow(restults_window)
	IJ.run("Close")

	imp.close()
	imp = IJ.getImage()
	title = imp.title
	if os.path.exists(mapped_images_dir + title):
		os.remove(mapped_images_dir + title)
	IJ.saveAsTiff(imp, mapped_images_dir + title)
	imp.close()
################################################################################

def saveResults(imp, directory):
  if not IJ.isResultsWindow():
    sys.exit("Results Table is not open")
  current_image = imp.title
  a = current_image[ : current_image.rfind(".tif")]
  IJ.saveAs("Results", directory + a + ".csv")
  IJ.selectWindow("Results")
  IJ.run("Close")

################################################################################

def main(threshold, min_size, max_size, remove_last_slice = False):
  IJ.run("3D OC Options", "volume surface nb_of_obj._voxels nb_of_surf._voxels integrated_density mean_gray_value std_dev_gray_value median_gray_value minimum_gray_value maximum_gray_value centroid mean_distance_to_surface std_dev_distance_to_surface median_distance_to_surface centre_of_mass bounding_box dots_size=5 font_size=10 show_numbers white_numbers store_results_within_a_table_named_after_the_image_(macro_friendly) redirect_to=none")
  IJ.run("Set Measurements...", "area mean centroid redirect=None decimal=6")

  Commands.closeAll()
  selected_dir = IJ.getDirectory("Select Directory")
  print(selected_dir)
  selected_dir = selected_dir + "/"
  dir_list = list()
  file_type = "processed_images"

  if selected_dir.endswith(file_type + "/"):
		dir_list.append(selected_dir)
  else:
		dir_list = listDir(selected_dir, file_type, recursive = True)
  print(dir_list)
  for dir in dir_list:
    print(dir)
    cd_dir = dir + "/cd/"
    print(cd_dir)
    makeDir(cd_dir)
    image_list = listDir(dir, file_type = ".tiff", recursive = False)
    for i in image_list:
      print(i)
      now = time.time()
      IJ.open(i)
      imp = IJ.getImage()
      IJ.run(imp, "Measure", "")
      saveResults(imp, cd_dir)
      #processImage(imp, threshold, min_size, max_size, remove_last_slice)
      later = time.time()
      difference = int(later - now)
      #time.sleep(difference/10)
      print("The time difference is " + str(difference))

#imp = IJ.getImage()
#processImage(imp, threshold = 1000, min = 4, max = 25)

"""
now = time.time()

later = time.time()
difference = int(later - now)
"""

#main(threshold = 1000, min_size = 4, max_size = 25, remove_last_slice = True)
