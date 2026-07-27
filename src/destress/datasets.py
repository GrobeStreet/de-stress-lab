"""Built-in public summary datasets used by the flagship demonstration."""

from .data import AnisotropicBAO, BAODataset, IsotropicBAO

DESI_DR2_BAO = BAODataset.from_measurements(
    "DESI DR2 published BAO summaries",
    [
        IsotropicBAO("BGS z=0.295", 0.295, 7.942, 0.075),
        AnisotropicBAO("LRG1 z=0.510", 0.510, 13.588, 0.167, 21.863, 0.425, -0.459),
        AnisotropicBAO("LRG2 z=0.706", 0.706, 17.351, 0.177, 19.455, 0.330, -0.404),
        AnisotropicBAO(
            "LRG3+ELG1 z=0.934", 0.934, 21.576, 0.152, 17.641, 0.193, -0.416
        ),
        AnisotropicBAO("ELG2 z=1.321", 1.321, 27.601, 0.318, 14.176, 0.221, -0.434),
        AnisotropicBAO("QSO z=1.484", 1.484, 30.512, 0.760, 12.817, 0.516, -0.500),
        AnisotropicBAO("Lya z=2.330", 2.330, 38.988, 0.531, 8.632, 0.101, -0.431),
    ],
)

