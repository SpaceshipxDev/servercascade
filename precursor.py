import cadquery as cq
from cadquery import importers, exporters

workplane = importers.importStep("/Users/hashashin/Documents/useful_information/20250528-探野T4-3D打印手板加工/零件3D/4按键1.stp")
exporters.export(workplane, "test.stl")

