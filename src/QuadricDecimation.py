import vtk


def create_renderer():
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.1, 0.2, 0.4)
    return renderer


# 创建球体源数据
sphere = vtk.vtkSphereSource()
sphere.SetThetaResolution(50)
sphere.SetPhiResolution(50)
sphere.Update()

# 应用简化
decimation = vtk.vtkQuadricDecimation()
decimation.SetInputConnection(sphere.GetOutputPort())
decimation.SetTargetReduction(0.8)
decimation.Update()

# 创建原始模型的可视化管线
mapper_original = vtk.vtkPolyDataMapper()
mapper_original.SetInputData(sphere.GetOutput())

actor_original = vtk.vtkActor()
actor_original.SetMapper(mapper_original)

# 创建简化模型的可视化管线
mapper_decimated = vtk.vtkPolyDataMapper()
mapper_decimated.SetInputConnection(decimation.GetOutputPort())

actor_decimated = vtk.vtkActor()
actor_decimated.SetMapper(mapper_decimated)

# 创建两个渲染器，分别设置视口
renderer_original = create_renderer()
renderer_original.AddActor(actor_original)
renderer_original.SetViewport(0, 0, 0.5, 1)  # 左半部分

renderer_decimated = create_renderer()
renderer_decimated.AddActor(actor_decimated)
renderer_decimated.SetViewport(0.5, 0, 1, 1)  # 右半部分

# 创建窗口和交互器
window = vtk.vtkRenderWindow()
window.AddRenderer(renderer_original)
window.AddRenderer(renderer_decimated)
window.SetSize(1200, 600)
window.SetWindowName("Model Comparison")


# 添加文本标签
def add_text(renderer, text, position):
    text_actor = vtk.vtkTextActor()
    text_actor.SetInput(text)
    text_actor.GetTextProperty().SetFontSize(20)
    text_actor.GetTextProperty().SetColor(1.0, 1.0, 1.0)
    text_actor.SetPosition(position, 10)
    renderer.AddActor2D(text_actor)


add_text(renderer_original, f"Original: {sphere.GetOutput().GetNumberOfPolys()} polygons", 10)
add_text(renderer_decimated, f"Decimated: {decimation.GetOutput().GetNumberOfPolys()} polygons", 10)

# 设置相同的相机视角
renderer_decimated.SetActiveCamera(renderer_original.GetActiveCamera())

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)

# 添加交互式缩放和旋转控制
style = vtk.vtkInteractorStyleTrackballCamera()
interactor.SetInteractorStyle(style)

# 初始化并启动
renderer_original.ResetCamera()
interactor.Initialize()
window.Render()
interactor.Start()
