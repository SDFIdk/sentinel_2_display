from osgeo import gdal
import os

#STRAIGHT OUTTA CHATGPT, VERIFY THAT THIS EVEN WORKS

class NDVITools:

    @staticmethod
    def vrt_from_bands(bands, output_vrt):
        options = gdal.BuildVRTOptions(separate=True)
        gdal.BuildVRT(output_vrt, bands, options=options)

    def build_ndvi_vrt(self):
        """
        Builds a VRT with separate bands from a list of dataset paths and calculates NDVI.
        Output name optional, defaults to NDVI.vrt.
        """

        ndvi_vrts = []
        for tile in self.available_tiles:
            b4 = os.path.join(tile, 'B04_10m.jp2')
            b8 = os.path.join(tile, 'B08_10m.jp2')

            ndvi_bands = os.path.join(tile, 'ndvi_bands.vrt')
            ndvi_vrt = os.path.join(tile, 'ndvi.vrt')

            # Step 1: Create VRT with separate bands
            NDVITools.vrt_from_bands([b8, b4], ndvi_bands)

            # Step 2: Open the VRT and read the bands
            vrt_ds = gdal.Open(ndvi_bands)
            band_b8 = vrt_ds.GetRasterBand(1).ReadAsArray()
            band_b4 = vrt_ds.GetRasterBand(2).ReadAsArray()

            # Step 3: Calculate NDVI
            ndvi = (band_b8 - band_b4) / (band_b8 + band_b4)

            # Step 4: Create the output VRT file
            driver = gdal.GetDriverByName('VRT')
            ndvi_ds = driver.Create(ndvi_vrt, vrt_ds.RasterXSize, vrt_ds.RasterYSize, 1, gdal.GDT_Float32)
            ndvi_band = ndvi_ds.GetRasterBand(1)
            ndvi_band.WriteArray(ndvi)

            # Set no data value if necessary
            ndvi_band.SetNoDataValue(-9999)

            # Copy georeferencing information from the input VRT
            ndvi_ds.SetGeoTransform(vrt_ds.GetGeoTransform())
            ndvi_ds.SetProjection(vrt_ds.GetProjection())

            # Clean up
            ndvi_band.FlushCache()
            vrt_ds = None
            ndvi_ds = None

            ndvi_vrts.append(ndvi_vrt)

        return ndvi_vrts