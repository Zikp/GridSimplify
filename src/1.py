import vtk
import numpy as np

# 创建点
points = vtk.vtkPoints()
n = 5  # 每边5个点
spacing = 1.0  # 点之间的间距

# 创建规则的点阵
for z in range(n):
    for y in range(n):
        for x in range(n):
            points.InsertNextPoint(x*spacing, y*spacing, z*spacing)

# 创建非结构网格
grid = vtk.vtkUnstructuredGrid()
grid.SetPoints(points)

# 创建六面体单元和三角形面
for z in range(n-1):
    for y in range(n-1):
        for x in range(n-1):
            # 计算当前立方体的8个顶点索引
            p0 = x + y*n + z*n*n
            p1 = p0 + 1
            p2 = p0 + n
            p3 = p2 + 1
            p4 = p0 + n*n
            p5 = p4 + 1
            p6 = p4 + n
            p7 = p6 + 1
            
            # 创建六面体
            hexahedron = vtk.vtkHexahedron()
            vertex_ids = [p0, p1, p3, p2, p4, p5, p7, p6]
            for i, vid in enumerate(vertex_ids):
                hexahedron.GetPointIds().SetId(i, vid)
            grid.InsertNextCell(hexahedron.GetCellType(), hexahedron.GetPointIds())

            # 定义每个面的顶点
            faces = [
                [p0, p1, p3, p2],  # 前
                [p4, p5, p7, p6],  # 后
                [p0, p2, p6, p4],  # 左
                [p1, p3, p7, p5],  # 右
                [p0, p1, p5, p4],  # 下
                [p2, p3, p7, p6]   # 上
            ]

            # 为每个面创建两个三角形
            for face in faces:
                # 第一个三角形
                triangle1 = vtk.vtkTriangle()
                triangle1.GetPointIds().SetId(0, face[0])
                triangle1.GetPointIds().SetId(1, face[1])
                triangle1.GetPointIds().SetId(2, face[2])
                grid.InsertNextCell(triangle1.GetCellType(), triangle1.GetPointIds())
                
                # 第二个三角形
                triangle2 = vtk.vtkTriangle()
                triangle2.GetPointIds().SetId(0, face[0])
                triangle2.GetPointIds().SetId(1, face[2])
                triangle2.GetPointIds().SetId(2, face[3])
                grid.InsertNextCell(triangle2.GetCellType(), triangle2.GetPointIds())

# 创建mapper和actor
mapper = vtk.vtkDataSetMapper()
mapper.SetInputData(grid)

actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(0.8, 0.2, 0.1)
actor.GetProperty().SetOpacity(0.7)
actor.GetProperty().SetRepresentationToSurface()

# 创建渲染器
renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
# 启用渐变背景
renderer.GradientBackgroundOn()
# 设置渐变颜色
renderer.SetBackground(0.0, 0.0, 0.8)  # 底部颜色(深蓝)
renderer.SetBackground2(1.0, 1.0, 1.0)  # 顶部颜色(白色)

# 创建渲染窗口
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindow.SetSize(800, 600)

print("点的数量:", grid.GetNumberOfPoints())
print("单元的数量:", grid.GetNumberOfCells())

# 创建交互器
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(renderWindow)

# 设置交互器样式
style = vtk.vtkInteractorStyleTrackballCamera()
interactor.SetInteractorStyle(style)

# 初始化交互器并开始事件循环
interactor.Initialize()
renderWindow.Render()
interactor.Start()
