# -*- encoding: utf-8 -*-
'''
Created on 2024/09/11 11:24:16

@author: BOJUN WANG
'''
from osgeo import gdal

def Convert_Coor(source_tif:str, target_tif:str):
    '''
    :param source_tif: 原始的栅格影像, 文件格式为 tiff
    :param target_tif: 目标的栅格影像, 文件格式为 tiff
    :return:
    '''
    # print("开始执行栅格重投影")
    gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8")
    gdalwarp_option = gdal.WarpOptions(
        format='Gtiff',
        dstSRS='+proj=utm +zone=52 +datum=WGS84 +units=m +no_defs'
    )
    out_ds = gdal.Warp(target_tif, source_tif, options=gdalwarp_option)
    out_ds.FlushCache()
    del out_ds
    # print("栅格重投影成功")


def Convert_Coor_with_SHP(source_shp:str, target_shp:str):
    '''
    :param source_shp: 原始的shp文件
    :param target_shp: 投影后的shp文件
    :return:
    '''
    # print("开始执行矢量重投影")
    # gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8")
    gdal.SetConfigOption("SHAPE_ENCODING", "UTF-8")
    vector_options = gdal.VectorTranslateOptions(
        dstSRS='+proj=utm +zone=52 +datum=WGS84 +units=m +no_defs'
    )
    out_ds = gdal.VectorTranslate(target_shp, source_shp, options=vector_options)
    out_ds.FlushCache()
    del out_ds
    # print("执行矢量投影成功")


