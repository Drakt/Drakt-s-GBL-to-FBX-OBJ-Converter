# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['C:/Users/adam_/Downloads/drakts-ascent-capacitor/glb_to_fbx_app.py'],
    pathex=['C:/Users/adam_/Downloads/drakts-ascent-capacitor'],
    binaries=[
        ('C:/Users/adam_/Downloads/drakts-ascent-capacitor/native_fbx_converter.exe', '.'),
        ('C:/Program Files/Autodesk/FBX/FBX SDK/2020.3.10/lib/x64/release/libfbxsdk.dll', '.'),
        ('C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Redist/MSVC/14.44.35112/x64/Microsoft.VC143.CRT/msvcp140.dll', '.'),
        ('C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Redist/MSVC/14.44.35112/x64/Microsoft.VC143.CRT/vcruntime140.dll', '.'),
        ('C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Redist/MSVC/14.44.35112/x64/Microsoft.VC143.CRT/vcruntime140_1.dll', '.'),
    ],
    datas=[
        ('C:/Program Files/Autodesk/FBX/FBX SDK/2020.3.10/License.rtf', '.'),
        ('C:/Users/adam_/Downloads/drakts-ascent-capacitor/drakt_logo.png', '.'),
        ('C:/Users/adam_/Downloads/drakts-ascent-capacitor/drakt_mmo_skin.png', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='GLB-to-FBX-Professional',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
