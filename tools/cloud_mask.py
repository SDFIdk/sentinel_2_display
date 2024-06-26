from tools.cloud_mask_tools import CMTools

class CloudMask():

    def __init__(self, available_tiles, scl_band, qc_band, today):
        self.available_tiles = available_tiles
        self.scl = scl_band
        self.qc = qc_band
        self.today = today


    def scl_to_cloudmask(self):

        #current code saves all inbetween steps as seperate files. In future, maybe remove excess?

        scl_tif = "SCL01.tif"
        calc_path = "gdal_calc.py"

        command = [
            calc_path,
            "--format=GTiff",
            "-A", self.scl,
            "--outfile", scl_tif,
            "--calc", "(A<=6)*0 + (A>=7)*(A<=10)*1 + (A>10)*0"
        ]

        CMTools.run_gdal_calc(self.scl, scl_tif, command)
        CMTools.resolution_averaging(scl_tif, "SCL01_250m.tif")
        CMTools.polygonalize_tif("SCL01_250m.tif", "cloud_and_nodata.shp")
        CMTools.buffer_nodata("SCL01_250m.tif", "cloud_and_nodata_buffer.shp")

        command = [
            calc_path,
            "--format=GTiff",
            "--type=Float32"
            "-A", self.scl,
            "--outfile", "footprint_60.tif",
            "--calc", f"0*(A<=0.01) + (A>0.01)*{self.today}"
        ]
        CMTools.run_gdal_calc(self.qc, "footprint_60.tif", command)
        CMTools.run_gdal_calc("cloud_and_nodata_buffer.shp", "footprint_60.tif", self.today, inverse = True)
        CMTools.run_gdal_calc("cloud_and_nodata_buffer.shp", "footprint_60.tif", 0)
        CMTools.polygonalize_tif("footprint_60.tif", "out_buffer.shp")
        CMTools.translate_vector("footprint_60.tif", "out_buffer32", "EPSG:32632")
        CMTools.translate_vector("footprint_60.tif", "out_buffer33", "EPSG:32633")
        



        return scl_tif


# call Gdal_polygonize -mask footprint_60.tif footprint_60.tif out_buffer.shp
# call ogr2ogr -t_srs epsg:32632 out_buffer32.shp out_buffer.shp
# call ogr2ogr -t_srs epsg:32633 out_buffer33.shp out_buffer.shp
