parent_dir = getDirectory("Select Parent Directory");

arr = newArray(0);

mvd2_dir_list = listDir(parent_dir, arr);

for (k = 0; k < mvd2_dir_list.length; k++) {
	mvd2_dir = mvd2_dir_list[k];
	tiff_dir = mvd2_dir + "tiff" + File.separator;
  if (!File.exists(tiff_dir)){
    stitched_dir = tiff_dir + "stitched_images" + File.separator;
    File.makeDirectory(tiff_dir);
    File.makeDirectory(stitched_dir);
    tiff_list = VolocityFileSave(mvd2_dir, tiff_dir);
    mainStitching(tiff_list, tiff_dir, stitched_dir);
  }
}


function mainStitching(tiff_list, tiff_dir, stitched_dir) {
  temp_dir = tiff_dir + "TEMP"+ File.separator;
  File.makeDirectory(temp_dir);
  for (i = 0; i<tiff_list.length; i+=2){
    print(tiff_list[i]);
    exec("cp", tiff_dir + tiff_list[i], temp_dir + tiff_list[i]);
    exec("cp", tiff_dir + tiff_list[i+1], temp_dir + tiff_list[i+1]);
    stitch(temp_dir, stitched_dir);
  }
  otherList = getFileList(temp_dir);
  for (l = 0; l<otherList.length; l++) {
    ok = File.delete(temp_dir + otherList[l]);
  }
  ok = File.delete(temp_dir);
}


function stitch(temp_dir, stitched_dir) {
  run("Grid/Collection stitching", "type=[Unknown position] order=[All files in directory] directory=[" + temp_dir + "] output_textfile_name=TileConfiguration.txt fusion_method=[Linear Blending] regression_threshold=0.30 max/avg_displacement_threshold=2.50 absolute_displacement_threshold=3.50 computation_parameters=[Save computation time (but use more RAM)] image_output=[Fuse and display]");
  
//  wait(60000);
  temp_tiff_list = getFileList(temp_dir);
  b = "";
  c = "";
  for (j=0; j<temp_tiff_list.length; j++) {
    c = temp_tiff_list[j];
    if(endsWith(c, ".tiff")) {
      if( j > 0 ){
              b = b + "-" + substring(temp_tiff_list[j], 0, indexOf(temp_tiff_list[j], "_"));
            }else{
              b = b + substring(temp_tiff_list[j], 0, indexOf(temp_tiff_list[j], "_"));
            }
    }
    ok = File.delete(temp_dir + temp_tiff_list[j]);
  }
  myFile = b + ".tiff";
  saveAs("Tiff", stitched_dir + myFile);
  run("Close");

}





//**************************************************************************************************


function listDir(dir, arr) {
  list = getFileList(dir);
  for (i=0; i<list.length; i++) {
    if (endsWith(list[i], "/")) {
      arr = listDir(""+dir+list[i], arr);
    }else {
      if (endsWith(list[i], ".mvd2")) {
        if (arr.length == 0){
          arr = appendArray(arr, dir);
        }else{
          if (arr[arr.length - 1] != dir){
            arr = appendArray(arr, dir);
          } 
          
        }
      }
    }
    
  }
  return arr;
}


function appendArray(arr, value) {
  newLength = arr.length;
  arr2 = newArray(newLength + 1);
  if (newLength > 0) {
    for (j=0; j<newLength; j++)
        arr2[j] = arr[j];
  }
  arr2[newLength] = value;
  return arr2;
}

function VolocityFileSave(mvd2_dir, tiff_dir) {
    if (nImages > 0) {
        close("*");
    }
  files_list = getFileList(mvd2_dir);
  for (n = 0; n<files_list.length; n++){
    if (endsWith(files_list[n], ".mvd2")){
      mvd2_file = mvd2_dir + files_list[n];
      run("Bio-Formats Importer", "open=[" + mvd2_file + "] autoscale color_mode=Composite open_all_series rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT");
      genotype = substring(files_list[n], 0, lastIndexOf(files_list[n], "."));
      images_list = getList("image.titles");
      if (images_list.length%2 == 1){
        exit("There are odd number of images");
      }
      tiff_list = newArray(images_list.length);
      for (o = 0; o < images_list.length; o++) {
        tiff_name = IJ.pad(o+1, 3) + "_" + genotype + ".tiff";
        tiff_save_name = tiff_dir + IJ.pad(o+1, 3) + "_" + genotype + ".tiff";
        tiff_list[o] = tiff_name;
        selectImage(images_list[o]);
        saveAs("Tiff", tiff_save_name);
        run("Close");
      }
    }
  }
  return tiff_list;
}