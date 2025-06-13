import cadquery as cq
from cadquery import importers, exporters

shape = importers.importStep("/Users/hashashin/Documents/useful_information/20250528-探野T4-3D打印手板加工/零件3D/13镜头.stp")

asm = cq.Assembly()
asm.add(shape)

exporters.export(
    asm,
    "output_model.glb",
    exporters.ExportTypes.GLTF,   # explicit — works on every 2.x build
    tolerance=0.05,
    angularTolerance=0.3,
    binary=True                   # binary ⇒ GLB; omit for .gltf text
)
print("✓ exported to output_model.glb")