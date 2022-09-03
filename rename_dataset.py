import shutil
import os
from tqdm import tqdm

SRC_TIF_DIR = "F:\Tesis S2\dataset\SpaceNet\/tiff_preprocessed"
SRC_GEOJSON_DIR = "F:\Tesis S2\dataset\SpaceNet\geojson_preprocessed"
DEST_TIF_DIR = "F:\Tesis S2\dataset\SpaceNet\/train_dataset\/tiff_rgb"
DEST_GEOJSON_DIR = "F:\Tesis S2\dataset\SpaceNet\/train_dataset\geojson"

TIF_PREFIX = "RGB-PanSharpen_"
GEOJSON_PREFIX = "buildings_"
num = 1

for image_file in tqdm(os.listdir(SRC_TIF_DIR)):
    file_withouth_prefix = os.path.splitext(image_file)[0].replace(TIF_PREFIX,'')

    src_geojson_file = os.path.join(SRC_GEOJSON_DIR, GEOJSON_PREFIX+file_withouth_prefix+'.geojson')
    src_tif_file = os.path.join(SRC_TIF_DIR, image_file)

    NEW_FILE_PREFIX = "RGB-IMAGE-{}".format(num)
    dest_geojson_file = os.path.join(DEST_GEOJSON_DIR, NEW_FILE_PREFIX+'.geojson')
    dest_tif_file = os.path.join(DEST_TIF_DIR, NEW_FILE_PREFIX+'.tif')

    shutil.copy(src_geojson_file, dest_geojson_file)
    shutil.copy(src_tif_file, dest_tif_file)

    num += 1






