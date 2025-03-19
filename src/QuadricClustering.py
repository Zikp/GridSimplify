import vtk


def create_renderer():
    """创建渲染器"""
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.1, 0.2, 0.4)
    return renderer


def create_multiblock_data():
    """创建多块网格数据"""
    # 创建几何体
    cube = vtk.vtkCubeSource()
    cube.SetCenter(0, 0, 0)

    sphere = vtk.vtkSphereSource()
    sphere.SetCenter(2, 0, 0)
    sphere.SetRadius(0.8)
    sphere.SetThetaResolution(20)
    sphere.SetPhiResolution(20)

    cylinder = vtk.vtkCylinderSource()
    cylinder.SetCenter(-2, 0, 0)
    cylinder.SetRadius(0.6)
    cylinder.SetHeight(2)
    cylinder.SetResolution(20)

    # 更新源数据
    cube.Update()
    sphere.Update()
    cylinder.Update()

    # 创建多块数据集
    mb = vtk.vtkMultiBlockDataSet()
    mb.SetNumberOfBlocks(3)
    mb.SetBlock(0, cube.GetOutput())
    mb.SetBlock(1, sphere.GetOutput())
    mb.SetBlock(2, cylinder.GetOutput())

    return mb


def create_merged_polydata(multiblock):
    """合并多块数据为单一PolyData"""
    append = vtk.vtkAppendPolyData()

    iterator = multiblock.NewIterator()
    iterator.InitTraversal()
    while not iterator.IsDoneWithTraversal():
        data = iterator.GetCurrentDataObject()
        if isinstance(data, vtk.vtkPolyData):
            append.AddInputData(data)
        iterator.GoToNextItem()

    append.Update()
    return append.GetOutput()


# 创建多块数据
multiblock = create_multiblock_data()
merged_data = create_merged_polydata(multiblock)

# 应用简化
clustering = vtk.vtkQuadricClustering()
clustering.SetInputData(merged_data)
clustering.SetNumberOfXDivisions(10)
clustering.SetNumberOfYDivisions(10)
clustering.SetNumberOfZDivisions(10)
clustering.Update()

# 设置原始模型的可视化管线
mapper_original = vtk.vtkCompositePolyDataMapper()
mapper_original.SetInputDataObject(multiblock)

actor_original = vtk.vtkActor()
actor_original.SetMapper(mapper_original)

# 设置简化模型的可视化管线
mapper_simplified = vtk.vtkPolyDataMapper()
mapper_simplified.SetInputConnection(clustering.GetOutputPort())

actor_simplified = vtk.vtkActor()
actor_simplified.SetMapper(mapper_simplified)

# 创建渲染器
renderer_left = create_renderer()
renderer_left.AddActor(actor_original)
renderer_left.SetViewport(0, 0, 0.5, 1)

renderer_right = create_renderer()
renderer_right.AddActor(actor_simplified)
renderer_right.SetViewport(0.5, 0, 1, 1)

# 创建窗口
window = vtk.vtkRenderWindow()
window.AddRenderer(renderer_left)
window.AddRenderer(renderer_right)
window.SetSize(1200, 600)
window.SetWindowName("MultiBlock Model Comparison")


# 添加信息显示文本
def create_text_actor(text, position):
    text_actor = vtk.vtkTextActor()
    text_actor.SetInput(text)
    text_actor.GetTextProperty().SetFontSize(20)
    text_actor.GetTextProperty().SetColor(1.0, 1.0, 1.0)
    text_actor.SetPosition(position, 10)
    return text_actor


original_polys = merged_data.GetNumberOfPolys()
simplified_polys = clustering.GetOutput().GetNumberOfPolys()

renderer_left.AddActor2D(create_text_actor(f"Original: {original_polys} polygons", 10))
renderer_right.AddActor2D(create_text_actor(f"Simplified: {simplified_polys} polygons", 10))

# 同步相机视角
renderer_right.SetActiveCamera(renderer_left.GetActiveCamera())

# 设置交互器
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)
interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

# 初始化和启动
renderer_left.ResetCamera()
interactor.Initialize()
window.Render()
interactor.Start()