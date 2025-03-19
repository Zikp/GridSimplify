import vtk

def simplify_volume_mesh(input_mesh, reduction_rate=0.5, grid_resolution=50):
    """
    体网格轻量化处理
    Args:
        input_mesh: vtkUnstructuredGrid 输入体网格
        reduction_rate: float 简化率(0-1)
        grid_resolution: int 网格分辨率
    Returns:
        vtkUnstructuredGrid 简化后的体网格
    """
    # 1. 提取表面
    geometry = vtk.vtkGeometryFilter()
    geometry.SetInputData(input_mesh)
    geometry.Update()

    # 2. 网格简化
    simplifier = vtk.vtkQuadricClustering()
    simplifier.SetInputData(geometry.GetOutput())
    simplifier.SetNumberOfXDivisions(grid_resolution)
    simplifier.SetNumberOfYDivisions(grid_resolution)
    simplifier.SetNumberOfZDivisions(grid_resolution)
    simplifier.Update()

    # 3. 清理重复点
    cleaner = vtk.vtkCleanPolyData()
    cleaner.SetInputData(simplifier.GetOutput())
    cleaner.Update()

    # 4. 重建体网格
    delaunay = vtk.vtkDelaunay3D()
    delaunay.SetInputData(cleaner.GetOutput())
    delaunay.Update()

    return delaunay.GetOutput()

# 使用示例
def main():
    # 读取输入网格
    reader = vtk.vtkUnstructuredGridReader()
    reader.SetFileName("input.vtk")
    reader.Update()
    
    # 执行简化
    simplified_mesh = simplify_volume_mesh(reader.GetOutput())
    
    # 保存结果
    writer = vtk.vtkUnstructuredGridWriter()
    writer.SetFileName("simplified.vtk")
    writer.SetInputData(simplified_mesh)
    writer.Write()

if __name__ == "__main__":
    main()
    