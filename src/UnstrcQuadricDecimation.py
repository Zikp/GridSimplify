import numpy as np
from vtkmodules.util.numpy_support import numpy_to_vtk
from vtkmodules.vtkCommonDataModel import vtkUnstructuredGrid, vtkPolyData, vtkCellArray
from vtkmodules.vtkFiltersCore import vtkAppendFilter, vtkTriangleFilter, vtkUnstructuredGridQuadricDecimation
from vtkmodules.vtkFiltersGeometry import vtkGeometryFilter
from vtkmodules.vtkIOLegacy import vtkPolyDataWriter
from vtkmodules.vtkCommonCore import vtkPoints, vtkIdList
from vtkmodules.vtkCommonDataModel import vtkTetra


def create_large_unstructured_grid(num_points=1000, num_cells=500):
    """创建一个包含大量点和单元的示例非结构化网格"""
    points = vtkPoints()
    cells = vtkCellArray()

    # 创建点
    for i in range(num_points):
        x, y, z = np.random.rand(3)
        points.InsertNextPoint(x, y, z)

    # 创建四面体单元
    for i in range(num_cells):
        ids = np.random.choice(num_points, 4, replace=False)
        tetra = vtkTetra()
        for j in range(4):
            tetra.GetPointIds().SetId(j, ids[j])
        cells.InsertNextCell(tetra)

    grid = vtkUnstructuredGrid()
    grid.SetPoints(points)
    grid.SetCells(tetra.GetCellType(), cells)

    # 添加标量数据
    scalars = np.random.rand(num_points)
    vtk_scalars = numpy_to_vtk(scalars)
    grid.GetPointData().SetScalars(vtk_scalars)

    return grid


def save_to_vtk(unstructured_grid, filename):
    """保存为VTK格式"""
    geometry_filter = vtkGeometryFilter()
    geometry_filter.SetInputData(unstructured_grid)
    geometry_filter.Update()

    polydata = geometry_filter.GetOutput()

    writer = vtkPolyDataWriter()
    writer.SetFileName(filename)
    writer.SetInputData(polydata)
    writer.SetFileTypeToBinary()  # 或者使用 SetFileTypeToASCII()
    writer.Write()
    print(f"Saved to VTK file: {filename}")


def useQuadricDecimation(unstructuredGrid: vtkUnstructuredGrid, target_reduction=0.5):
    """使用 vtkUnstructuredGridQuadricDecimation 简化非结构化网格

    Args:
        unstructuredGrid: 输入的非结构化网格数据
        target_reduction: 目标简化率(0-1之间)

    Returns:
        vtkUnstructuredGrid: 简化后的网格
    """
    # 检查是否有标量数据
    if unstructuredGrid.GetPointData().GetScalars() is None:
        print("Warning: No scalar data found, adding default scalar values...")
        # 添加默认标量数据
        n_points = unstructuredGrid.GetNumberOfPoints()
        scalars = np.ones(n_points)
        unstructuredGrid.GetPointData().SetScalars(numpy_to_vtk(scalars))

    decimator = vtkUnstructuredGridQuadricDecimation()
    decimator.SetInputData(unstructuredGrid)
    decimator.SetTargetReduction(target_reduction)

    # 设置网格质量控制参数
    decimator.SetBoundaryWeight(100)  # 提高边界保持权重

    try:
        decimator.Update()
        output = decimator.GetOutput()

        # 验证输出
        if output.GetNumberOfCells() == 0:
            raise RuntimeError("Decimation produced empty mesh")

        print(f"\nDecimation Results:")
        print(f"Original cells: {unstructuredGrid.GetNumberOfCells()}")
        print(f"Simplified cells: {output.GetNumberOfCells()}")
        print(f"Actual reduction: {1 - output.GetNumberOfCells() / unstructuredGrid.GetNumberOfCells():.2%}")

        return output

    except Exception as e:
        print(f"Decimation failed: {str(e)}")
        return unstructuredGrid


if __name__ == '__main__':
    # 创建示例非结构化网格
    unstructuredGrid = create_large_unstructured_grid()
    save_to_vtk(unstructuredGrid, "./mesh/unstrcMesh.vtk")

    # 设置目标简化率
    target_reduction = 0.5

    # 执行简化
    simplified_grid = useQuadricDecimation(unstructuredGrid, target_reduction)

    # 保存结果
    save_to_vtk(simplified_grid, "./mesh/unstrcMesh_simple.vtk")
