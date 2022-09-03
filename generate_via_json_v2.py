from webbrowser import get
import os
import json
import geoio
from tqdm import tqdm
from random import shuffle
# import numpy as np
import shutil
# import cv2 as cv

BUILDING_MASK_PATH_DIR = "F:\Tesis S2\dataset\SpaceNet\/train_dataset\/mask_png"
BUILDING_TIF_DIR = "F:\Tesis S2\dataset\SpaceNet\/train_dataset\/tiff_rgb"
BUILDING_PNG_DIR = "F:\Tesis S2\dataset\SpaceNet\/train_dataset\png_rgb"
PROCESSED_TRAIN_PATH = 'F:\Tesis S2\dataset\SpaceNet\/train_dataset\processed_png\/train'
PROCESSED_VAL_PATH = 'F:\Tesis S2\dataset\SpaceNet\/train_dataset\processed_png\/validation'
GEOJSON_DIR = "F:\Tesis S2\dataset\SpaceNet\/train_dataset\geojson"

VIA_JSON_FILE = "building_annotation.json"
IMG_WIDTH, IMG_HEIGHT = 650, 650

def get_mask(geojson_file):

    with open(os.path.join(GEOJSON_DIR, geojson_file)) as f:
        geojson_data = json.load(f)

    #load tif image
    tif_image_filename = os.path.splitext(geojson_file)[0]+'.tif'
    tif_image_data = geoio.GeoImage(
        os.path.join(BUILDING_TIF_DIR, tif_image_filename)
    )

    building_coordinates_list = []

    for data in geojson_data['features']:
        building_type = str(data['geometry']['type'])

        if building_type == "Point":
            pass
        elif building_type == "MultiPolygon":
            building_coordinate = data['geometry']['coordinates']
            for b in building_coordinate:
                building_coordinates_list.append(b)
        elif building_type == "Polygon":
            building_coordinates_list.append(data['geometry']['coordinates'])

    img_pixel_coord = []
    for building_coord in building_coordinates_list:
        building = []
        for coord in building_coord:
            
            xy_pixel_list = []

            for point in coord:
                x_pixel, y_pixel = tif_image_data.proj_to_raster(point[0], point[1])
                x_pixel = IMG_WIDTH-1 if x_pixel > IMG_WIDTH-1 else x_pixel
                y_pixel = IMG_HEIGHT-1 if y_pixel > IMG_HEIGHT-1 else y_pixel
                
                xy_pixel_list.append([x_pixel, y_pixel])

            building.append(xy_pixel_list)
        img_pixel_coord.append(building)

    return img_pixel_coord


def generate_via_json(geojson_files, out_path, out_json, img_dir):
    json_annot = {}
    with open(os.path.join(out_path, out_json), 'w') as js_file:
        for geojson_file in tqdm(geojson_files):
            # mask_path = os.path.join(BUILDING_MASK_PATH_DIR, mask_file)
            # gray = cv.imread(mask_path)
            # imgray = cv.cvtColor(gray, cv.COLOR_BGR2GRAY)
            # _, thresh = cv.threshold(imgray, 127, 255, cv.THRESH_BINARY)
            # contours, _ = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

            # approx_contours = [cv.approxPolyDP(
            #     c,
            #     100 * cv.arcLength(c, True)
            #     , True
            # ) for c in contours]

            approx_contours = get_mask(geojson_file)
            
            # for i in range(len(approx_contours)):
            #     # print(approx_contours[i])
            #     for building in approx_contours[i]:
            #         print(building)
            #         all_x = []
            #         all_y = []
            #         for coord in building:
            #             all_x.append(coord[0])
            #             all_y.append(coord[1])
            #         print(all_y)


            if len(approx_contours) > 1:
                regions = [0 for i in range(len(approx_contours))]

                for i in range(len(approx_contours)):
                    shape_attributes = {}
                    region_attributes = {}
                    regions_i = {}

                    region_attributes['class'] = 'building'
                    shape_attributes['name'] = 'polygon'

                    for building in approx_contours[i]:

                        all_x = []
                        all_y = []

                        for coord in building:
                            all_x.append(coord[0])
                            all_y.append(coord[1])

                        shape_attributes['all_points_x'] = all_x
                        shape_attributes['all_points_y'] = all_y
                        
                        
                    regions_i['shape_attributes'] = shape_attributes
                    regions_i['region_attributes'] = region_attributes
                    regions[i] = regions_i
                

                image_filename = os.path.splitext(geojson_file)[0]+'.png'
                size = os.path.getsize(os.path.join(
                        img_dir,
                        image_filename
                        ))
                name = image_filename + str(size)

                json_mask = {}
                json_mask['filename'] = image_filename
                json_mask['size'] = str(size)
                json_mask['regions'] = regions
                json_mask['file_attributes'] = []
                
                json_annot[name] = json_mask

                shutil.copy(
                    os.path.join(img_dir, image_filename),
                    os.path.join(out_path, image_filename)
                )

        json.dump(json_annot, js_file, indent=4)



geojson_files = os.listdir(GEOJSON_DIR)
shuffle(geojson_files)

train_data_num = int(len(geojson_files) * 0.85)
validation_data_num = len(geojson_files) - train_data_num

train_data = geojson_files[0:train_data_num]
validation_data = geojson_files[train_data_num:]

#generate train data
print('GENERATE TRAINING DATA')
generate_via_json(train_data, PROCESSED_TRAIN_PATH, VIA_JSON_FILE, BUILDING_PNG_DIR)

#generate validation data
print('GENERATE VALIDATION DATA')
generate_via_json(validation_data, PROCESSED_VAL_PATH, VIA_JSON_FILE, BUILDING_PNG_DIR)

print('TOTAL TRAIN DATA: ', len(os.listdir(PROCESSED_TRAIN_PATH))-1)
print('TOTAL VALIDATION DATA: ', len(os.listdir(PROCESSED_VAL_PATH))-1)
