#include <fbxsdk.h>
#include <filesystem>
#include <iostream>
#include <string>

namespace fs = std::filesystem;

static void printError(const char* stage, FbxStatus& status) {
    std::cerr << stage << " failed: " << status.GetErrorString() << "\n";
}

int main(int argc, char** argv) {
    if (argc < 3) {
        std::cerr << "Usage: native_fbx_converter input.obj output.fbx\n";
        return 2;
    }
    const char* input = argv[1];
    const char* output = argv[2];

    FbxManager* manager = FbxManager::Create();
    if (!manager) {
        std::cerr << "Unable to create FBX manager.\n";
        return 3;
    }
    FbxIOSettings* settings = FbxIOSettings::Create(manager, IOSROOT);
    manager->SetIOSettings(settings);
    settings->SetBoolProp(IMP_FBX_MATERIAL, true);
    settings->SetBoolProp(IMP_FBX_TEXTURE, true);
    settings->SetBoolProp(IMP_FBX_LINK, true);
    settings->SetBoolProp(EXP_FBX_MATERIAL, true);
    settings->SetBoolProp(EXP_FBX_TEXTURE, true);
    settings->SetBoolProp(EXP_FBX_EMBEDDED, true);
    settings->SetBoolProp(EXP_FBX_SHAPE, true);
    settings->SetBoolProp(EXP_FBX_MODEL, true);

    FbxScene* scene = FbxScene::Create(manager, "GLB-to-FBX AccuRIG Export");
    FbxImporter* importer = FbxImporter::Create(manager, "");
    if (!importer->Initialize(input, -1, settings)) {
        printError("OBJ import", importer->GetStatus());
        importer->Destroy();
        scene->Destroy();
        manager->Destroy();
        return 4;
    }
    if (!importer->Import(scene)) {
        printError("OBJ import", importer->GetStatus());
        importer->Destroy();
        scene->Destroy();
        manager->Destroy();
        return 5;
    }
    importer->Destroy();

    // AccuRIG treats imported characters as Y-up. Keep the OBJ's Y-up
    // geometry and declare the same axis system in the FBX metadata.
    FbxGlobalSettings& global = scene->GetGlobalSettings();
    global.SetSystemUnit(FbxSystemUnit(1.0));
    global.SetAxisSystem(FbxAxisSystem(FbxAxisSystem::eMayaYUp));

    FbxExporter* exporter = FbxExporter::Create(manager, "");
    const int format = manager->GetIOPluginRegistry()->FindWriterIDByDescription("FBX binary (*.fbx)");
    if (!exporter->Initialize(output, format, settings)) {
        printError("FBX export", exporter->GetStatus());
        exporter->Destroy();
        scene->Destroy();
        manager->Destroy();
        return 6;
    }
    if (!exporter->Export(scene)) {
        printError("FBX export", exporter->GetStatus());
        exporter->Destroy();
        scene->Destroy();
        manager->Destroy();
        return 7;
    }
    exporter->Destroy();
    scene->Destroy();
    manager->Destroy();
    std::cout << "FBX export complete\n";
    return 0;
}
