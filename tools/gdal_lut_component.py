import subprocess
from osgeo import gdal

def build_lut_vrt(input_tif):
    """
    Applies the same process as run_gdal_lut.bat on a single RGBI tif.
    Outputs are extrapolated from input and stored in same directory.
    Returns path to final output
    """

    eightbit_output = input_tif.replace(".tif", "_8bit.tif")

    gdal.Translate(
        eightbit_output,
        input_tif,
        outputType=gdal.GDT_Byte,
        scaleParams=[
            [0, 7500, 0, 255],
            [0, 7500, 0, 255],
            [0, 7500, 0, 255],
            [0, 10000, 0, 255]
        ]
    )

    lut_files = [
        "constants/lut_1.txt",
        "constants/lut_2.txt",
        "constants/lut_3.txt",
        "constants/lut_4.txt",
    ]

    # install gdal lut somehow? Can this be a file to be included in the package like calc?
    # is it related to this https://github.com/sudhirmurthy/gdal-examples/blob/master/gdal_lut.py   ?
    for i, lut_file in enumerate(lut_files, start=1):
        output_lut_tif = f"32UMF_RGBI_8bit_{i}.tif"
        subprocess.run([
            "gdal_lut",
            eightbit_output,
            "-srcband", str(i), 
            output_lut_tif,
            "-lutfile", lut_file
        ])

    input_lut_tifs = [
        input_tif.replace(".tif", "_8bit_1.tif"),
        input_tif.replace(".tif", "_8bit_2.tif"),
        input_tif.replace(".tif", "_8bit_3.tif"),
        input_tif.replace(".tif", "_8bit_4.tif"),
    ]

    output_vrt = eightbit_output.replace(".tif", "_lut.vrt")
    gdal.BuildVRT(output_vrt, input_lut_tifs, separate=True)
    return output_vrt
