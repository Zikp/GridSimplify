# -*- coding: UTF-8 -*-

"""
@File    :   Open3DTest.py
@Time    :   2025/3/20 14:48
@Author  :   zhoujie
@Version :   1.0
@Contact :   1336231025@qq.com
@Desc    :   None
"""
import pyvista as pv
import numpy as np
from tqdm import tqdm


def process_cfd_mesh(input_file: str,
                     output_file: str,
                     target_reduction: float = 0.5):
    """
    Process CFD mesh with triangulation

    Parameters:
        input_file (str): Input mesh file path
        output_file (str): Output mesh file path
        target_reduction (float): Reduction ratio (0-1)
    """
    try:
        # Read mesh
        print("Reading mesh...")
        mesh = pv.read(input_file)

        # Convert to surface if needed
        if isinstance(mesh, pv.UnstructuredGrid):
            print("Converting to surface mesh...")
            mesh = mesh.extract_surface()

        # Triangulate the surface
        print("Triangulating surface...")
        triangulated = mesh.triangulate()

        # Verify triangulation
        if not triangulated.is_all_triangles:
            raise ValueError("Failed to triangulate mesh completely")

        print("Simplifying mesh...")
        # Now we can decimate
        simplified = triangulated.decimate(target_reduction)

        # Save result
        simplified.save(output_file)

        # Print statistics
        print(f"\nMesh Statistics:")
        print(f"Original points: {mesh.n_points}")
        print(f"Simplified points: {simplified.n_points}")
        print(f"Reduction achieved: {1 - simplified.n_points / mesh.n_points:.2%}")

        return simplified

    except Exception as e:
        print(f"Error processing mesh: {str(e)}")
        raise


def simplify_volume_mesh(input_file, output_file, target_ratio=0.5):
    """使用 PyVista 简化体网格"""
    # 读取网格
    mesh = pv.read(input_file)

    # 提取内部单元
    internal = mesh.extract_cells(mesh.cell_centers().points)

    # 执行简化
    simplified = internal.decimate(target_reduction=1 - target_ratio)

    # 保存结果
    simplified.save(output_file)

    return simplified


if __name__ == "__main__":
    # Process mesh
    result = process_cfd_mesh('../mesh/elbow.vtk', '../mesh/elbow_simplify.vtk')
    result1 = simplify_volume_mesh('../mesh/elbow.vtk', '../mesh/elbow_simplify.vtk')

    # Visualize comparison
    plotter = pv.Plotter(shape=(1, 2))

    # Original mesh
    plotter.subplot(0, 0)
    original = pv.read("../mesh/elbow.vtk").extract_surface().triangulate()
    plotter.add_mesh(original, show_edges=True, label='p', show_scalar_bar=True)
    plotter.add_text("Original")

    # Simplified mesh
    plotter.subplot(0, 1)
    plotter.add_mesh(result1, show_edges=True)
    plotter.add_text("Simplified")

    plotter.link_views()
    plotter.show()

