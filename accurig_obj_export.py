from pathlib import Path
import trimesh


def export_accurig_obj(source, output_dir, target_height_cm=150):
    source = Path(source)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    scene = trimesh.load(str(source), force="scene")
    mesh = scene.to_geometry() if hasattr(scene, "to_geometry") else scene.dump(concatenate=True)
    height = float(mesh.bounds[1][1] - mesh.bounds[0][1])
    if height > 0:
        mesh.apply_translation([0, -float(mesh.bounds[0][1]), 0])
        mesh.apply_scale(float(target_height_cm) / height)
    base_name = "ForestGoblin_AccuRIG"
    obj_text, resources = trimesh.exchange.obj.export_obj(
        mesh, include_normals=True, include_color=False, include_texture=True,
        return_texture=True, mtl_name=f"{base_name}.mtl"
    )
    obj_path = output_dir / f"{base_name}.obj"
    obj_path.write_text(obj_text, encoding="utf-8")
    paths = [obj_path]
    for name, content in resources.items():
        if name.endswith(".mtl"):
            path = output_dir / f"{base_name}.mtl"
        elif name.endswith(".png"):
            path = output_dir / name
        else:
            path = output_dir / name
        path.write_bytes(content if isinstance(content, bytes) else bytes(content))
        paths.append(path)
    material = getattr(mesh.visual, "material", None)
    material_data = getattr(material, "_data", {}) or {}
    diffuse = material_data.get("baseColorTexture")
    if diffuse is not None:
        texture_dir = output_dir / base_name
        texture_dir.mkdir(exist_ok=True)
        diffuse_path = texture_dir / "AccuRIG_Diffuse.jpg"
        diffuse.convert("RGB").save(diffuse_path, quality=95, optimize=True)
        mtl_path = output_dir / f"{base_name}.mtl"
        mtl_path.write_text(
            f"newmtl material\nKa 1.000000 1.000000 1.000000\nKd 1.000000 1.000000 1.000000\nKs 0.000000 0.000000 0.000000\nd 1.000000\nmap_Kd {base_name}/AccuRIG_Diffuse.jpg\n",
            encoding="utf-8",
        )
        paths.append(diffuse_path)
    return obj_path, paths
