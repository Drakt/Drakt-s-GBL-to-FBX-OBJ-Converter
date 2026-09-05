# Professional GLB to FBX Converter

The standalone professional build uses Autodesk FBX SDK for the FBX writing stage. Blender is not required.

It converts a GLB into an AccuRIG-oriented FBX package, preserves the extracted textures, converts the scene to Z-up, and scales the character to the requested height in centimetres. The output folder also contains a textured OBJ/MTL fallback.

The Autodesk FBX SDK license notice is included with the application package.

This is a Windows desktop utility for converting static GLB files to binary FBX while exporting embedded textures and a matching `.fbm` folder. It includes its own conversion runtime and does not require Blender.

## Run it

1. Double-click `GLB-to-FBX-Standalone.exe`.
2. Select a `.glb` file, choose an output folder, set the target height in centimeters, and click **Convert to FBX**. The default is 150 cm (1.5 m).
3. Keep the generated FBX and texture files together. The app also creates an `*_AccuRIG.obj` plus its MTL and texture as a fallback for AccuRIG. The optional ZIP keeps everything packaged together.

The standalone converter currently targets static mesh GLB files. Skeletal rigs, skin weights, morph targets, and animation are not yet included.
