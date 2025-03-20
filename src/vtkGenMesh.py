# -*- coding: UTF-8 -*-

"""
@File    :   vtkGenMesh.py
@Time    :   2025/3/20 17:25
@Author  :   zhoujie
@Version :   1.0
@Contact :   1336231025@qq.com
@Desc    :   None
"""
import pyvista as pv
import vtk
import pyvista as pv
import numpy as np


class VTKMeshGenerator:
    """VTK几何网格生成器"""

    def __init__(self):
        self.mesh = None

    def generate_surface_mesh(self, geometry, element_size=1.0):
        """表面网格生成"""
        # 使用 Delaunay2D 进行表面网格剖分
        delaunay = vtk.vtkDelaunay2D()
        delaunay.SetInputData(geometry)
        delaunay.SetTolerance(element_size)
        delaunay.SetProjectionPlaneMode(vtk.VTK_BEST_FITTING_PLANE)
        delaunay.Update()

        # 转换为 PyVista 对象
        self.mesh = pv.wrap(delaunay.GetOutput())
        return self.mesh

    def generate_volume_mesh(self, geometry, element_size=1.0):
        """体网格生成"""
        # 使用 Delaunay3D 进行体网格剖分
        tetra = vtk.vtkDelaunay3D()
        tetra.SetInputData(geometry)
        tetra.SetTolerance(element_size)
        tetra.SetAlpha(0)  # 0表示生成凸包
        tetra.BoundingTriangulationOff()
        tetra.Update()

        # 转换为 PyVista 对象
        self.mesh = pv.wrap(tetra.GetOutput())
        return self.mesh


# 创建一个球体几何
sphere = pv.Sphere(radius=1.0, theta_resolution=20, phi_resolution=20)

# 初始化网格生成器
generator = VTKMeshGenerator()

# 生成表面网格
surface_mesh = generator.generate_surface_mesh(sphere)

# 生成体网格
volume_mesh = generator.generate_volume_mesh(sphere)

# 保存结果
surface_mesh.save("sphere_surface.vtk")
volume_mesh.save("sphere_volume.vtk")
