from osgeo import gdal, ogr
import subprocess
import os
import pathlib

class CMTools():    

    def resolution_averaging(input_file, output_file, xRes = 250, yRes = 250):

        """
        Resamples file to new spatial resolution
        """
        
        options = gdal.TranslateOptions(
            xRes=xRes,
            yRes=yRes,
            resampleAlg="average"
        )

        gdal.Translate(output_file, input_file, options=options)


    def polygonalize_tif(input_file, output_file):
        src_ds = gdal.Open(input_file)
        src_band = src_ds.GetRasterBand(1)

        driver = ogr.GetDriverByName("ESRI Shapefile")
        out_ds = driver.CreateDataSource(output_file)
        out_layer = out_ds.CreateLayer(output_file, geom_type=ogr.wkbPolygon)

        field = ogr.FieldDefn("DN", ogr.OFTInteger)
        out_layer.CreateField(field)

        gdal.Polygonize(src_band, src_band, out_layer, 0, [], callback=None)


    def buffer_nodata(input_file, output_file):

        sql_query = "select ST_buffer(geometry, 1000) as geometry FROM cloud_and_nodata"
        gdal.VectorTranslate(
            output_file,
            input_file,
            format="ESRI Shapefile",
            SQLStatement=sql_query,
            SQLDialect="sqlite"
        )


    def burn_cloudmask(input_shapefile, output_file, burn_value, inverse = False):

        dst_ds = gdal.Open(output_file, gdal.GA_Update)
        gdal.Rasterize(dst_ds, input_shapefile, burnValues=[burn_value], inverse=inverse)


    def translate_vector(input_vector, output_vector, target_srs):
        options = gdal.VectorTranslateOptions(
            dstSRS=target_srs
        )
        gdal.VectorTranslate(
            output_vector,
            input_vector,
            options=options
        )


    def update_footprint(footprint, destination_dir, today):
            
        pathlib.Path(destination_dir).mkdir(parents=True, exist_ok=True)

        footprint_temp = f"{destination_dir}/footprint.tif"
        footprint_shape = f"{destination_dir}/footprint_{today}.shp"
        
        gdal.Warp(
            footprint_temp,
            footprint,
            srcNodata = 0,
            resampleAlg='near',
        )

        src_ds = gdal.Open(footprint_temp)
        src_band = src_ds.GetRasterBand(1)

        driver = ogr.GetDriverByName("ESRI Shapefile")
        out_ds = driver.CreateDataSource(footprint_shape)
        out_layer = out_ds.CreateLayer(f"footprint_{today}", geom_type=ogr.wkbPolygon)

        field = ogr.FieldDefn("DN", ogr.OFTInteger)
        out_layer.CreateField(field)

        gdal.Polygonize(src_band, src_band, out_layer, 0, [], callback=None)

        return footprint_shape
