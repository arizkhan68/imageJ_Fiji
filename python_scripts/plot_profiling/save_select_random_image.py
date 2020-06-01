from ij import WindowManager, IJ
import random
imp = IJ.getImage()
image = imp.title
IJ.selectWindow(image)
IJ.run("Save")
IJ.run("Close")
open_images = WindowManager.getImageTitles()
nImages = len(open_images)
IJ.setTool("rectangle")
print(nImages)
if nImages > 0:
  n = random.randint(0, nImages-1)
  IJ.selectWindow(open_images[n])
#  IJ.run("In [+]", "")
#  IJ.run("In [+]", "")
  #print(n)