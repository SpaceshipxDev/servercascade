import cadquery as cq
from cadquery import importers, exporters

workplane = importers.importStep("/Users/hashashin/Documents/useful_information/20250528-探野T4-3D打印手板加工/零件3D/13镜头.stp")

asm = cq.Assembly()
asm.add(workplane.val())

exporters.export(
    asm,
    "output_model.glb",
    tolerance=0.05,
    angularTolerance=0.3
)

print("✓ exported to output_model.glb")