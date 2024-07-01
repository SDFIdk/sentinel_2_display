class Constants:
    """
    Constants for SDFI Labs Sentinel-2 display
    """

    def get_tile_list():
        """
        List of tile ids of Sentinel-2 scenes covering Denmark
        """
        return [
            "32UMF",
            "32UMG",
            "32UNF",
            "32UNG",
            "32UPF",
            "32UPG",
            "32VMH",
            "32VMJ",
            "32VNH",
            "32VNJ",
            "32VNK",
            "32VPH",
            "32VPJ",
            "32VPK",
            "33UUA",
            "33UUB",
            "33UVA",
            "33UVB",
            "33UWA",
            "33UWB",
            "33VUC",
            "33VUD"
        ]
    
    def get_s2_granules():
        """
        List of standard band names in a Sentinel-2 product
        """
        return [
            "B02_10m.jp2",
            "B03_10m.jp2",
            "B04_10m.jp2",
            "B08_10m.jp2",
            "SCL_20m.jp2",
            "B01_20m.jp2",
            "B05_20m.jp2",
            "B06_20m.jp2",
            "B07_20m.jp2",
            "B8A_20m.jp2",
            "B11_20m.jp2",
            "B12_20m.jp2",
            "WVP_10m.jp2",
            "AOT_10m.jp2",
            "B09_60m.jp2"
        ]
    
    def get_UTM32_tiles():
        """
        Tiles in UTM32 crs
        """
        return [
            "T32UMF",
            "T32UMG",
            "T32UNF",
            "T32UNG",
            "T32UPF",
            "T32UPG",
            "T32VMH",
            "T32VMJ",
            "T32VNH",
            "T32VNJ",
            "T32VNK",
            "T32VPH",
            "T32VPJ",
            "T32VPK",
        ]
    
    def get_UTM33_tiles():
        """
        Tiles in UTM33 crs
        """
        return [
            "T33UUA",
            "T33UUB",
            "T33UVA",
            "T33UVB",
            "T33UWA",
            "T33UWB",
            "T33VUC",
            "T33VUD",
        ]
