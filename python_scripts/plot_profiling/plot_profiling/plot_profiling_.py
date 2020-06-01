from __future__ import division
import sys, os, os.path, re, time, shutil, csv

from ij.process import ImageProcessor
from ij import ImagePlus, IJ, WindowManager, plugin
from ij.gui import ProfilePlot, Roi, PolygonRoi
from ij.plugin import Commands

cd = 25
sync_dropbox = False
primary_staining = "PROM-1_HA"

stainings = ["PROM-1_HA", "WAPL-1", "DAPI"]
#stainings = ["NHR-48_HA", "WAPL-1", "DAPI"]
# stainings = ["PROM-1_HA", "pSUN-1", "WAPL-1", "DAPI"]
#############################################################
def mean(x):
  return(sum(x)/len(x))

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

def saveResults(imp, directory, sync_dropbox=False, dropbox_marker_dir=None):
  current_image = imp.title
  a = current_image[ : current_image.rfind(".tif")]
  csv_file = directory + a + ".csv"
  IJ.saveAs("Results", csv_file)
  if sync_dropbox:
    IJ.saveAs("Results", dropbox_marker_dir + a + ".csv")
  
  IJ.selectWindow("Results")
  IJ.run("Close")
  return(csv_file)

################################################################################

def makeDropboxDir(image_dir, genotype):
  dir_list = image_dir.split("/")
  regex = re.compile("[0-1]?[0-9]\.[0-3]?[0-9]\.[2]?0?[0-9][0-9].*")
  base_dir = filter(regex.match, dir_list)
  base_dir = base_dir[0]
  dropbox_exp_dir = dropbox_dir + base_dir + "/"
  makeDir(dropbox_exp_dir)
  regex = re.compile("replicate_[1-9]")
  repl_dir = filter(regex.match, dir_list)
  if repl_dir:
    dropbox_repl_dir = dropbox_exp_dir + repl_dir[0] + "/"
    makeDir(dropbox_repl_dir)
  dropbox_genotype_dir = dropbox_repl_dir + genotype + "/"
  makeDir(dropbox_genotype_dir)
  dropbox_profile_dir = dropbox_genotype_dir + "plot_profile/"
  makeDir(dropbox_profile_dir)
  dropbox_marker_dir = dropbox_genotype_dir + "markers/"
  makeDir(dropbox_marker_dir)
  dropbox_dirs = [dropbox_marker_dir, dropbox_profile_dir]
  return(dropbox_dirs)

#########################################################################

def saveProfile(nch, top, bottom, staining, genotype, staining_dir, image_name, sync_dropbox = False, dropbox_staining_dir = None, cd = cd):
  for j in range(bottom, top+1):
    imp1 = IJ.getImage()
    imp1.setC(nch)
    imp1.setZ(j)
    pp1 = ProfilePlot(imp1)
    s = "profile" + str(j)
    exec(s + " = pp1.getProfile()")
  
  file_name = image_name[ : (image_name.rfind('.tif'))] + "_" + staining + "_cd_" + str(cd) + ".csv"
  file_save = staining_dir + file_name
  with open(file_save, "w") as text_file:
    text_file.write("x,value")
#  text_file.close()
  with open(file_save, "a") as text_file:
    for j in range(len(eval("profile" + str(top)))):
#      print([profile1[j], profile2[j] ], max([profile1[j], profile2[j] ]))
      x = list()
      
      for k in range(bottom, top+1):
        x.append("profile" + str(k) + "[j]")
      #print(x)
      text_file.write("\n" + str(j) + "," + str(eval(max(x))))
#  text_file.close()
  #print(top, bottom)
  if sync_dropbox:
    dropbox_file_save =  dropbox_staining_dir + file_name
    shutil.copyfile(file_save, dropbox_file_save)

##############################################################################################

#############################################################################################


if sync_dropbox:
  dropbox_folder="Dropbox/Acad/computational_work/R/protein_expression_plots/"
  dropbox_folder = dropbox_folder + primary_staining + "_analysis/"
  dropbox_dir = "/home/areeba/" + dropbox_folder
  with open('/etc/os-release') as f:
    first_line = f.readline().strip()
  if first_line.split('"')[1] == "Ubuntu":
    dropbox_dir = "/media/areeba/0532f45d-0f7e-4dad-b42d-b2b36e8b8b56/areeba/" + dropbox_folder

IJ.run("3D OC Options", "volume surface nb_of_obj._voxels nb_of_surf._voxels integrated_density mean_gray_value std_dev_gray_value median_gray_value minimum_gray_value maximum_gray_value centroid mean_distance_to_surface std_dev_distance_to_surface median_distance_to_surface centre_of_mass bounding_box dots_size=5 font_size=10 show_numbers white_numbers store_results_within_a_table_named_after_the_image_(macro_friendly) redirect_to=none")
IJ.run("Set Measurements...", "centroid redirect=None decimal=6")
if IJ.isResultsWindow():
  IJ.selectWindow(restults_window)
  IJ.run("Close")

def processImage():
  imp = IJ.getImage()
  image_name = imp.title
  nChannels = imp.NChannels
  if nChannels != len(stainings):
    sys.exit("There are " + str(nChannels) + " channels in this image, as against " + str(len(stainings)) + " stainings you have specified. \nPlease fix this issue in the script and then re-run it?")
  IJ.run("Save")
  image_dir = IJ.getDirectory("image")
  genotype = image_dir[0 : (len(image_dir)-1)]
  genotype = genotype[(genotype.rfind('/')+1) : ]
  IJ.run(imp, "Measure", "")
  marker_dir = image_dir + "markers/"
  profile_dir = image_dir + "plot_profile/"
  makeDir(marker_dir, profile_dir)
  if sync_dropbox:
    dropbox_dirs = makeDropboxDir(image_dir, genotype)
    dropbox_marker_dir = dropbox_dirs[0]
    dropbox_profile_dir = dropbox_dirs[1]
    csv_file = saveResults(imp, marker_dir, sync_dropbox, dropbox_marker_dir)
  else:
    csv_file = saveResults(imp, marker_dir)
  
  xpoints = list(); ypoints = list(); slices = list()
  
  with open(csv_file, 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)
    for line in csv_reader:
      xpoints.append(int(float(line[1])))
      ypoints.append(int(float(line[2])))
      slices.append(int(line[4]))

  #start with 25
  if len(xpoints) < 26:
    imp.setRoi(PolygonRoi(xpoints,ypoints,Roi.POLYLINE))
    print("Not enough cds")
    imp.close()
    return()  
  start_time= time.time()  
  for cd in range(25, len(xpoints)-1, 5):
    xpolypoints = xpoints[1:(cd+2)]  # ignore the first (0th) dot 
    ypolypoints = ypoints[1:(cd+2)]
    polyslices = slices[1:(cd+2)]
    if max(slices) == 1:
      top = 2
      bottom = 1
    else:
      top = max(polyslices)
      if min(polyslices) < top:
        bottom = min(polyslices)
      else:
        bottom = top - 1
    IJ.run(imp, "Line Width...", "line=75")
    imp.setRoi(PolygonRoi(xpolypoints,ypolypoints,Roi.POLYLINE))
    #getProfile(cd)
    for i, staining in enumerate(stainings):
      staining_dir = profile_dir + staining + "/"
      makeDir(staining_dir)
      nChannel = i + 1
      if sync_dropbox:
        dropbox_staining_dir = dropbox_profile_dir + staining + "/"
        makeDir(dropbox_staining_dir)
        saveProfile(nChannel, top, bottom, staining, genotype, staining_dir, image_name, True, dropbox_staining_dir, cd = cd)
      else:
        saveProfile(nChannel, top, bottom, staining, genotype, staining_dir, image_name, cd = cd)
  end_time= time.time()
  print(int(end_time-start_time))
  imp.close()



def main():
  if (WindowManager.getImageCount() > 0):
    processImage()
#  if (WindowManager.getImageCount() > 0):
#    for image in range(WindowManager.getImageCount()):
#      processImage()
  else:
    selected_dir = IJ.getDirectory("Select Directory")
    if not selected_dir.endswith("/"):
      selected_dir = selected_dir + "/"
    dir_list = list()
    file_type = "stitched_images"
    
    if selected_dir.endswith(file_type + "/"):
      dir_list.append(selected_dir)
      print(dir_list)
    else:
      dir_list = listDir(selected_dir, file_type, recursive = True)
    print(dir_list)
    if len(dir_list) > 0:
      for dir in dir_list:
        genotype_dirs = list()
        filenames= os.listdir(dir)
        print(filenames)

        for filename in filenames:
        	print(filename)
        	if os.path.isdir(os.path.join(os.path.abspath(dir), filename)):
        		genotype_dirs.append(os.path.join(os.path.abspath(dir), filename))
        for genotype_dir in genotype_dirs:
        	print(genotype_dir)
        	image_list = listDir(genotype_dir, file_type = ".tiff", recursive = False)
        	for image in image_list:
					  IJ.open(image)
					  processImage()
    else:
      image_list = listDir(selected_dir, file_type = ".tiff", recursive = False)
      for image in image_list:
        IJ.open(image)
        processImage()
main()  
