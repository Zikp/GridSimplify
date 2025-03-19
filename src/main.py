import threading
import time
import pyvista as pv
import numpy as np
from vtkmodules.util.numpy_support import numpy_to_vtk

from vtkmodules.vtkCommonDataModel import vtkMultiBlockDataSet, vtkUnstructuredGrid, vtkPolyData, vtkCell
from vtkmodules.vtkFiltersCore import vtkAppendFilter, vtkDecimatePro, vtkQuadricDecimation, vtkTriangleFilter, \
    vtkQuadricClustering, vtkUnstructuredGridQuadricDecimation
from vtkmodules.vtkFiltersGeometry import vtkGeometryFilter
from vtkmodules.vtkIOLegacy import vtkPolyDataWriter
from IO.TecplotReaderPlugin import TecplotReaderPlugin


def save_to_tecplot(vtk_data, filename):
    """将VTK数据转换并保存为Tecplot格式"""
    # 转换为PyVista对象
    pv_data = pv.wrap(vtk_data)

    # 保存为Tecplot格式
    pv_data.save(filename)
    print(f"Saved to file: {filename}")


def save_to_vtk(polydata, filename):
    """保存为VTK格式"""
    writer = vtkPolyDataWriter()
    writer.SetFileName(filename)
    writer.SetInputData(polydata)
    writer.SetFileTypeToBinary()  # 或者使用 SetFileTypeToASCII()
    # writer.WriteToOutputStringOn()
    writer.WriteArrayMetaDataOn()
    # writer.Wr
    writer.Write()
    print(f"Saved to VTK file: {filename}")


def set_mesh_to_triangles(polydata):
    e = vtkTriangleFilter()
    e.SetInputData(polydata)
    e.Update()
    return e.GetOutput()


def analyze_mesh_divisions(unstructured_grid: vtkUnstructuredGrid):
    # 获取所有单元的中心点
    n_cells = unstructured_grid.GetNumberOfCells()
    centers = np.zeros((n_cells, 3))

    for i in range(n_cells):
        cell = unstructured_grid.GetCell(i)
        # Calculate center manually
        points = cell.GetPoints()
        n_points = points.GetNumberOfPoints()
        center = np.zeros(3)

        # Average all points to get center
        for j in range(n_points):
            point = points.GetPoint(j)
            center[0] += point[0]
            center[1] += point[1]
            center[2] += point[2]

        center /= n_points
        centers[i] = center

    # 使用唯一点计数估算分割数
    unique_x = len(np.unique(centers[:, 0].round(decimals=5)))
    unique_y = len(np.unique(centers[:, 1].round(decimals=5)))
    unique_z = len(np.unique(centers[:, 2].round(decimals=5)))

    print(f"\n网格分析结果:")
    print(f"X方向估计单元数: {unique_x}")
    print(f"Y方向估计单元数: {unique_y}")
    print(f"Z方向估计单元数: {unique_z}")

    return unique_x, unique_y, unique_z


def useDecimatePro(polyData, target_reduction=0.8):
    _polyData: vtkPolyData = set_mesh_to_triangles(polyData)

    e = _polyData.GetNumberOfPoints()
    r = _polyData.GetNumberOfCells()
    print(f"三角化后单元的数量：{r}")
    print(f"三角化后点的数量：{e}")

    decimator = vtkDecimatePro()
    decimator.SetInputData(_polyData)
    decimator.SetTargetReduction(target_reduction)
    decimator.PreserveTopologyOn()
    decimator.SplittingOff()  # 禁止分裂操作
    decimator.BoundaryVertexDeletionOff()
    decimator.Update()

    return decimator.GetOutput()


def useQuadricDecimation(polyData, target_reduction=0.8):
    # _polyData = set_mesh_to_triangles(polyData)

    # 检查是否有标量数据
    if polyData.GetPointData().GetScalars() is None:
        print("Warning: No scalar data found, adding default scalar values...")
        # 添加默认标量数据
        n_points = polyData.GetNumberOfPoints()
        scalars = np.ones(n_points)
        polyData.GetPointData().SetScalars(numpy_to_vtk(scalars))

    decimator = vtkUnstructuredGridQuadricDecimation()
    decimator.SetInputData(polyData)

    decimator.SetTargetReduction(target_reduction)

    # 设置网格质量控制
    # decimator.SetBoundaryWeight(100)  # 提高边界保持权重
    decimator.Update()
    output = decimator.GetOutput()

    return output


def useQuadricClustering(polyData, target_reduction=0.8):
    x, y, z = analyze_mesh_divisions(polyData)
    print(f"x方向上的单元数{x}")
    print(f"y方向上的单元数{y}")
    print(f"z方向上的单元数{z}")

    clustering = vtkQuadricClustering()
    clustering.SetInputData(polyData)
    clustering.SetNumberOfXDivisions(int(x * (1 - target_reduction)))
    clustering.SetNumberOfYDivisions(int(y * (1 - target_reduction)))
    clustering.SetNumberOfZDivisions(int(z * (1 - target_reduction)))
    # 保持点数据和单元数据
    clustering.CopyCellDataOn()
    clustering.SetUseInputPoints(True)
    # 开启特征保持
    clustering.UseFeatureEdgesOn()
    # 开启边界保持
    clustering.UseInternalTrianglesOn()
    clustering.Update()

    return clustering.GetOutput()


def __importGrid_TecplotBin(fpath):
    # 1. 读取网格
    reader = TecplotReaderPlugin()
    print(f'读取网格({fpath})')
    th = threading.Thread(target=reader.setFiles, args=([fpath],))
    th.start()
    while th.is_alive():
        time.sleep(0.5)
        print('.')
    print(f'网格读取完成({fpath})')
    cellSize = 0
    pointSize = 0

    timeList = reader.GetTimeSets()
    multiBlickData: vtkMultiBlockDataSet = reader.getMultiBlockDataSetByTime(0)
    appendFilter = vtkAppendFilter()
    if multiBlickData:
        for indexBlock in range(multiBlickData.GetNumberOfBlocks()):
            block = multiBlickData.GetBlock(indexBlock)
            cellSize += multiBlickData.GetBlock(indexBlock).GetNumberOfCells()
            pointSize += multiBlickData.GetBlock(indexBlock).GetNumberOfPoints()
            appendFilter.AddInputData(block)
        print(f'网格轻量化前：')
        print(f'Mesh Cell Number is: {cellSize}')
        print(f'Mesh Point Number is: {pointSize}\n')
        appendFilter.Update()
        dataSet: vtkUnstructuredGrid = appendFilter.GetOutput()

        # 2. 转换为 vtkPolyData
        geometryFilter = vtkGeometryFilter()
        geometryFilter.SetInputData(dataSet)
        geometryFilter.Update()
        polyData: vtkPolyData = geometryFilter.GetOutput()

        # save_to_vtk(polyData, "./mesh/field_node_bin.vtk")

        return polyData, dataSet


if __name__ == '__main__':
    polyData, unstrDataset = __importGrid_TecplotBin('./mesh/field_node_bin.plt')
    target_reduction = 0.8

    algMap = {
        'DecimatePro': useDecimatePro,
        # 'QuadricDecimation': useQuadricDecimation,
        'QuadricClustering': useQuadricClustering
    }
    try:
        for k, v in algMap.items():
            startTime = time.time()

            simpleDataSet = v(polyData, target_reduction)
            cellSize = simpleDataSet.GetNumberOfCells()
            pointSize = simpleDataSet.GetNumberOfPoints()
            print(f'算法:{k}开始执行：\n网格轻量化后(轻量化系数{target_reduction})')
            print(f'Mesh Cell Number is: {cellSize}')
            print(f'Mesh Point Number is: {pointSize}')

            endTime = time.time()
            print(f"算法:{k}  程序运行时间：{endTime - startTime}\n")

            save_to_vtk(simpleDataSet, f"./mesh/field_node_bin_{k}.vtk")

    except Exception as e:
        print(e)

    # simpleDataSet = useDecimatePro(polyData, target_reduction)
    # simpleDataSet = useQuadricDecimation(polyData, target_reduction)
    # simpleDataSet = useQuadricClustering(polyData, target_reduction)
