# -*- coding: UTF-8 -*-

"""
@File    :   Open3DTest.py
@Time    :   2025/3/20 14:48
@Author  :   zhoujie
@Version :   1.0
@Contact :   1336231025@qq.com
@Desc    :   None
"""
from pathlib import Path
import pyvista as pv
import open3d as o3d
import numpy as np


class CFDMeshSimplifier:
    """CFD网格简化处理类"""

    def __init__(self):
        self.supported_formats = ['.cgns', '.plt', '.vtk', '.vtu', '.vtp']

    def check_format(self, filename: str) -> bool:
        """检查文件格式是否支持"""
        return Path(filename).suffix.lower() in self.supported_formats

    def process_cfd_mesh(self,
                         input_file: str,
                         output_file: str,
                         target_ratio: float = 0.5,
                         method: str = 'pyvista'):
        """
        处理 CFD 网格文件

        Parameters:
            input_file: 输入文件路径
            output_file: 输出文件路径
            target_ratio: 简化比例 (0-1)
            method: 使用的简化方法 ('pyvista' or 'open3d')
        """
        if not self.check_format(input_file):
            raise ValueError(f"Unsupported format: {Path(input_file).suffix}")

        if method == 'pyvista':
            return self._process_with_pyvista(input_file, output_file, target_ratio)
        elif method == 'open3d':
            return self._process_with_open3d(input_file, output_file, target_ratio)
        else:
            raise ValueError(f"Unsupported method: {method}")

    def _process_with_pyvista(self, input_file, output_file, target_ratio):
        mesh = pv.read(input_file)
        simplified = mesh.decimate(1 - target_ratio)
        simplified.save(output_file)
        return simplified

    def _process_with_open3d(self, input_file, output_file, target_ratio):
        # 先读取输入文件
        mesh_pv = pv.read(input_file)

        # 将 PyVista 网格转换为 Open3D 格式
        vertices = np.array(mesh_pv.points)
        faces = np.array(mesh_pv.faces.reshape(-1, 4)[:, 1:4])  # 转换面片数据格式

        # 创建 Open3D 网格对象
        mesh = o3d.geometry.TriangleMesh()
        mesh.vertices = o3d.utility.Vector3dVector(vertices)
        mesh.triangles = o3d.utility.Vector3iVector(faces)

        # 执行网格简化
        simplified = mesh.simplify_quadric_decimation(
            int(len(mesh.triangles) * target_ratio)
        )

        # 将简化后的网格转回 PyVista 格式
        vertices_simplified = np.asarray(simplified.vertices)
        faces_simplified = np.asarray(simplified.triangles)

        # 创建 PyVista 网格对象（需要添加面片数量信息）
        faces_with_count = np.hstack((
            np.full((len(faces_simplified), 1), 3),  # 每个面片3个顶点
            faces_simplified
        ))
        mesh_out = pv.PolyData(vertices_simplified, faces=faces_with_count)

        # 保存结果
        mesh_out.save(output_file)

        return simplified


if __name__ == "__main__":
    # 创建简化器
    simplifier = CFDMeshSimplifier()

    # 处理 CGNS 文件
    simplifier.process_cfd_mesh(
        "../mesh/elbow.vtk",
        "../mesh/elbow-o3d-simple.vtk",
        target_ratio=0.3,
        method='open3d'
    )

    # 处理 PLOT3D 文件
    # simplifier.process_cfd_mesh(
    #     "flow.plt",
    #     "simplified.stl",
    #     target_ratio=0.5,
    #     method='open3d'
    # )
