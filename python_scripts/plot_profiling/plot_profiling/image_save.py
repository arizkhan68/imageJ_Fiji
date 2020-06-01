from ij import ImagePlus, IJ
imp = IJ.getImage()
IJ.run(imp, "Save", "")
IJ.run("Close")