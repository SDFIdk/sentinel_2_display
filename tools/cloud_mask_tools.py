from osgeo import gdal, ogr
import subprocess
import os
import pathlib

class CMTools():    

    def resolution_averaging(input_file, output_file):
        
        options = gdal.TranslateOptions(
            xRes=250,
            yRes=250,
            resampleAlg="average"
        )
        gdal.Translate(output_file, input_file, options=options)


    def polygonalize_tif(input_file, output_file, data_band = None):
        src_ds = gdal.Open(input_file)
        src_band = src_ds.GetRasterBand(1)

        if not data_band: data_band = os.path.splitext(data_band)[0]

        driver = ogr.GetDriverByName("ESRI Shapefile")
        out_ds = driver.CreateDataSource(output_file)
        out_layer = out_ds.CreateLayer(data_band, geom_type=ogr.wkbPolygon)

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


    def burn_cloudbuffer(input_shapefile, output_file, burn_value, inverse = False):

        src_ds = gdal.Open(output_file, gdal.GA_Update)
        gdal.Rasterize(src_ds, input_shapefile, burnValues=[burn_value], inverse=inverse)


    def translate_vector(input_file, output_file, target_srs):

        gdal.VectorTranslate(
            output_file,
            input_file,
            dstSRS=target_srs
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
