import vtk
from stl import mesh
from util import *
import numpy as np
from functools import reduce
import os

def save_png(output_file, renderWindow):
    store_renwin = vtk.vtkWindowToImageFilter()
    store_renwin.SetInput(renderWindow)
    #store_renwin.SetScale(1)
    store_renwin.SetScale(1)
    store_renwin.SetInputBufferTypeToRGB()
    store_renwin.ReadFrontBufferOff()
    store_renwin.Update()

    writer = vtk.vtkPNGWriter()
    writer.SetFileName(output_file)
    writer.SetInputData(store_renwin.GetOutput())
    writer.Write()


def drawing(msg, output_file, angle):
    data_matrix, x_max, x_min, y_max, y_min, z_max, z_min, q_max, q_min = msg[0], msg[1], msg[2], msg[3], msg[4], msg[
        5], msg[6], msg[7], msg[8]

    q_range = q_max - q_min
    x_range = x_max - x_min
    y_range = y_max - y_min
    z_range = z_max - z_min

    Renderer = vtk.vtkRenderer()
    Renderer.SetBackground(1.0, 1.0, 1.0)

    # Camera
    camera = Renderer.GetActiveCamera()
    camera.ParallelProjectionOn()
    camera.SetPosition(-10, 0, 0)
    '''
    if epoch == 0:
        camera.SetPosition(0, 0, 10)
    if epoch == 1:
        camera.SetPosition(0, 0, -10)
    if epoch == 2:
        camera.SetPosition(0, 10, 0)
    if epoch == 3:
        camera.SetPosition(0, -10, 0)
    if epoch == 4:
        camera.SetPosition(10, 0 , 0)
    if epoch == 5:
    '''


    # RenderWindow
    RenderWindow = vtk.vtkRenderWindow()
    RenderWindow.AddRenderer(Renderer)
    RenderWindow.SetSize(512, 512)
    RenderWindow.OffScreenRenderingOn()
    RenderWindow.Render()

    # Color
    LookupTable = vtk.vtkLookupTable()
    LookupTable.SetNumberOfTableValues(65536)#0-65535
    LookupTable.Build()
    for i in range(256):
        for j in range(256):
            k =  i * 256 + j
            LookupTable.SetTableValue(k,  0, i / 255.0, j / 255.0, 1.0)#自己设置的颜色表，所以应该没有线性这么一说

    # Poly
    for matrix_index, data_array in enumerate(data_matrix):
        data_array[:, :, 0] = (data_array[:, :, 0] - x_min) / x_range
        data_array[:, :, 1] = (data_array[:, :, 1] - y_min) / y_range
        data_array[:, :, 2] = (data_array[:, :, 2] - z_min) / z_range
        data_array[:, :, 7] = (data_array[:, :, 7] - q_min) / q_range

        datas = {}
        heat_flux = []
        points = vtk.vtkPoints()#几何结构
        cell_array = vtk.vtkCellArray()#拓扑结构
        point_id = 0
        for i in range(len(data_array)):
            polygon = vtk.vtkPolygon()
            polygon.GetPointIds().SetNumberOfIds(3)
            for j in range(3):
                if not (data_array[i, j, 0], data_array[i, j, 1], data_array[i, j, 2]) in datas:
                    heat_flux.append(data_array[i, j, 7])
                    datas[(data_array[i, j, 0], data_array[i, j, 1], data_array[i, j, 2])] = point_id
                    points.InsertNextPoint(data_array[i, j, 0], data_array[i, j, 1], data_array[i, j, 2])

                    point_id += 1
                polygon.GetPointIds().SetId(j, datas[(data_array[i, j, 0], data_array[i, j, 1], data_array[i, j, 2])])
            cell_array.InsertNextCell(polygon)
        stlPolyData = vtk.vtkPolyData()
        stlPolyData.SetPoints(points)
        stlPolyData.SetPolys(cell_array)


        weight = vtk.vtkDoubleArray()
        for i, heat_value in enumerate(heat_flux):
            weight.InsertNextValue(int(heat_value * 65534))


        DataSetSurfaceFilter = vtk.vtkDataSetSurfaceFilter()
        DataSetSurfaceFilter.SetInputData(stlPolyData)
        DataSetSurfaceFilter.Update()

        SmoothPolyDataFilter = vtk.vtkSmoothPolyDataFilter()
        SmoothPolyDataFilter.SetNumberOfIterations(30)
        SmoothPolyDataFilter.SetInputConnection(DataSetSurfaceFilter.GetOutputPort())
        SmoothPolyDataFilter.Update()

        PolyDataNormals = vtk.vtkPolyDataNormals()
        PolyDataNormals.SetInputConnection(SmoothPolyDataFilter.GetOutputPort())
        PolyDataNormals.FlipNormalsOn()
        PolyDataNormals.ComputeCellNormalsOn()
        PolyDataNormals.Update()

        # Mapper
        DataSetMapper = vtk.vtkDataSetMapper()
        DataSetMapper.SetInputConnection(PolyDataNormals.GetOutputPort())
        DataSetMapper.SetScalarRange(0, 65534)
        DataSetMapper.SetLookupTable(LookupTable)
        DataSetMapper.Update()

        Actor = vtk.vtkActor()
        Actor.SetMapper(DataSetMapper)
        Actor.GetProperty().LightingOff()
        Actor.RotateZ(-angle)
        stlPolyData.GetPointData().SetScalars(weight)
        Renderer.AddActor(Actor)


    Renderer.ResetCamera()
    camera.SetParallelScale(0.7)
    DataSetSurfaceFilter.Update()
    save_png(output_file, RenderWindow)


    del camera
    del DataSetMapper
    del Actor
    del Renderer
    del RenderWindow





def write_filename_to_txt(output_txt_path, file_name):
    f = open(output_txt_path, 'a')
    file_name = file_name + '\n'
    f.write(file_name)
    f.close()


def write_condition_to_txt(output_txt_path1, conditions):
    f = open(output_txt_path1, 'a')
    header = 'max_x=' + str(conditions[0]) + '\n'
    f.write(header)
    header = 'min_x=' + str(conditions[1]) + '\n'
    f.write(header)
    header = 'max_y=' + str(conditions[2]) + '\n'
    f.write(header)
    header = 'min_y=' + str(conditions[3]) + '\n'
    f.write(header)
    header = 'max_z=' + str(conditions[4]) + '\n'
    f.write(header)
    header = 'min_z=' + str(conditions[5]) + '\n'
    f.write(header)
    header = 'max_q=' + str(conditions[6]) + '\n'
    f.write(header)
    header = 'min_q=' + str(conditions[7]) + '\n'
    f.write(header)
    f.close()

def master(input_path, output_path, output_txt_path, angle):
    file_name_list = os.listdir(input_path)
    for i, file_name in enumerate(file_name_list):
        input_file = input_path + file_name
        file_name = file_name.split('.hot')[0]
        write_filename_to_txt(output_txt_path, file_name)


        data_matrix, x_max, x_min, y_max, y_min, z_max, z_min, q_max, q_min = read_3D_flow_field_data(input_file)

        msg = []
        msg.append(data_matrix)
        msg.append(x_max)
        msg.append(x_min)
        msg.append(y_max)
        msg.append(y_min)
        msg.append(z_max)
        msg.append(z_min)
        msg.append(q_max)
        msg.append(q_min)


        for epoch in range(1):
            output_file = output_path + file_name
            output_file = output_file + '_' + str(epoch + 1) + '.png'
            drawing(msg, output_file, angle)

        conditions = []
        conditions.append(x_max)
        conditions.append(x_min)
        conditions.append(y_max)
        conditions.append(y_min)
        conditions.append(z_max)
        conditions.append(z_min)
        conditions.append(q_max)
        conditions.append(q_min)
        output_txt_path1 = output_path + file_name + '_' + str(0) + '.txt'
        write_condition_to_txt(output_txt_path1, conditions)
        print("-------数据生成完毕-------")
    print("------全部数据生成完毕-------")


if __name__ == '__main__':
    input_path = r'C:\Users\Lenovo\Desktop\data\\'
    file_name_list = os.listdir(input_path)
    output_path = r'C:\Users\Lenovo\Desktop\result\png_4\\'
    output_txt_path = r'C:\Users\Lenovo\Desktop\result\filenames_4.txt'
    conditions = []
    angle = 30
    master(input_path, output_path, output_txt_path, angle)