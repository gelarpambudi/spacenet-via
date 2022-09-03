import os
from tkinter.messagebox import NO
import numpy as np
from osgeo import gdal
from tqdm import tqdm

TIFF_DIR = "F:\Tesis S2\dataset\SpaceNet\AOI_4_Shanghai_Test_public\RGB-PanSharpen"
PNG_DIR = "F:\Tesis S2\dataset\SpaceNet\AOI_4_Shanghai_Test_public\png_rgb"
band_dst_min = 0
band_dst_max = 255


def convert_to_png(input_img, output_img, rescale_type, percentiles=[2, 98]):
    band_list = []
    scale_params_list = []
    input_raster = gdal.Open(input_img)
    for bandID in range(input_raster.RasterCount):
        bandID += 1
        band_list.append(bandID)
        band = input_raster.GetRasterBand(bandID)
        
        if rescale_type == "rescale":
            band_min = band.GetMinimum()
            band_max = band.GetMaximum()
            if band_min is None or band_max is None:
                (band_min, band_max) = band.ComputeRasterMinMax(1)
            
            band_array = band.ReadAsArray()
            band_min = np.percentile(band_array.flatten(), percentiles[0])
            band_max = np.percentile(band_array.flatten(), percentiles[1])
        else:
            band_min, band_max = 0, 65535

        scale_params_list.append([
            band_min,
            band_max,
            band_dst_min,
            band_dst_max
        ])
    
    ds = gdal.Translate(
            output_img,
            input_img,
            options=gdal.TranslateOptions(
                format='png',
                outputType=gdal.GDT_Byte,
                scaleParams=scale_params_list,
                bandList=band_list
            ))
    ds = None


for file in tqdm(os.listdir(TIFF_DIR)):
    src_path = os.path.join(TIFF_DIR, file)
    dst_path = os.path.join(
        PNG_DIR,
        os.path.splitext(file)[0]+'.png'
    )
    convert_to_png(src_path, dst_path, "rescale", percentiles=[2, 98])