# Drakt GLB to FBX/OBJ Converter

Standalone Windows converter for preparing static GLB character models for AccuRIG.

## Download

The latest packaged build is in [`standalone/Drakt-MMO-Output-Cleanup-Final.zip`](standalone/Drakt-MMO-Output-Cleanup-Final.zip).

The ZIP contains the tested Windows executable and the Autodesk FBX SDK license notice. Blender is not required.

## Features

- Exports FBX, OBJ, or both formats.
- Preserves extracted textures and creates a matching `.fbm` folder.
- Converts the scene to a vertical, AccuRIG-friendly orientation.
- Scales the character to the requested height in centimetres.
- Includes a textured OBJ/MTL fallback and optional ZIP packaging.

The converter targets static mesh GLB files. Skeletal rigs, skin weights, morph targets, and animation are not included.
