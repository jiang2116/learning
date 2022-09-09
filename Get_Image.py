# coding:utf-8
import vtk
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


def drawing(input_file, output_file, epoch, angle):
    with open(input_file) as f:
        all_lines = f.read().splitlines()

    variables = all_lines[1]
    variables = variables.split('=')[-1].split(',')
    variables = [item.replace('"', '') for item in variables]

    blocks = []
    zone = all_lines[2]
    block_number = all_lines.count(zone)
    block_start_index = [index + 2 for index, value in enumerate(all_lines) if value == zone]
    block_end_index = [index - 3 for index in block_start_index[1:]]  # 每个block的起始和结束的行
    block_end_index.append(len(all_lines) - 1)

    for i in range(block_number):
        block_start, block_end = block_start_index[i], block_end_index[i]
        block_params = dict(item.split('=') for item in all_lines[block_start - 1].replace(' ', '').split(','))
        point_number = int(block_params['I']) * int(block_params['J'])
        block = np.array(reduce(lambda x, y: x + y.split(), all_lines[block_start: block_end + 1], []))
        block = block.astype('float64')
        if block_params['F'] == 'Block':
            block = block.reshape(-1, point_number)
            block = np.transpose(block)
        elif block_params['F'] == 'Point':
            block = block.reshape(point_number, -1)

        block_params['ID'] = i
        block_params['Point_number'] = point_number
        block_params['Data'] = block
        blocks.append(block_params)



    max_q = max([np.max(block['Data'][:, 4]) for block in blocks])
    min_q = min([np.min(block['Data'][:, 4]) for block in blocks])
    q_range = max_q - min_q
    #q_range = 125000

    max_x = max([np.max(block['Data'][:, 0]) for block in blocks])
    min_x = min([np.min(block['Data'][:, 0]) for block in blocks])
    x_range = max_x - min_x

    max_y = max([np.max(block['Data'][:, 1]) for block in blocks])
    min_y = min([np.min(block['Data'][:, 1]) for block in blocks])
    y_range = max_y - min_y

    max_z = max([np.max(block['Data'][:, 2]) for block in blocks])
    min_z = min([np.min(block['Data'][:, 2]) for block in blocks])
    z_range = max_z - min_z

    Renderer = vtk.vtkRenderer()
    Renderer.SetBackground(1.0, 1.0, 1.0)

    # Camera
    camera = Renderer.GetActiveCamera()
    camera.ParallelProjectionOn()

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
        camera.SetPosition(-10, 0, 0)
    if epoch == 6:
        camera.SetPosition(0, 0, 10)
    if epoch == 7:
        camera.SetPosition(0, 0, -10)
    if epoch == 8:
        camera.SetPosition(0, 10, 0)
    if epoch == 9:
        camera.SetPosition(0, -10, 0)
    if epoch == 10:
        camera.SetPosition(10, 0, 0)
    if epoch == 11:
        camera.SetPosition(-10, 0, 0)


    # RenderWindow
    RenderWindow = vtk.vtkRenderWindow()
    RenderWindow.AddRenderer(Renderer)
    RenderWindow.SetSize(512, 512)
    RenderWindow.OffScreenRenderingOn()
    RenderWindow.Render()

    # Color
    k = -1
    LookupTable = vtk.vtkLookupTable()
    LookupTable.SetNumberOfTableValues(65536)#0-65535
    LookupTable.Build()
    for i in range(256):
        for j in range(256):
            k =  i * 256 + j
            LookupTable.SetTableValue(k,  0, i / 255.0, j / 255.0, 1.0)#自己设置的颜色表，所以应该没有线性这么一说

    # Poly
    for i, item in enumerate(blocks):
        polydata = vtk.vtkStructuredGrid()
        #polydata1 = vtk.vtkUnstructuredGrid()
        points = vtk.vtkPoints()
        scalars = vtk.vtkDoubleArray()
        scalars.SetName('Dim_Q')

        block = item['Data']
        I, J = int(item['I']), int(item['J'])

        for data in block:
            data_x = float((data[0] - min_x) / x_range)
            data_y = float((data[1] - min_y) / y_range)
            data_z = float((data[2] - min_z) / z_range)
            points.InsertNextPoint(data_x, data_y, data_z)
            data_q = float((data[4] - min_q) / q_range)

            if epoch == 0:
                scalars.InsertNextValue(data_z * 65534)
            if epoch == 1:
                scalars.InsertNextValue(data_z * 65534)
            if epoch == 2:
                scalars.InsertNextValue(data_y * 65534)
            if epoch == 3:
                scalars.InsertNextValue(data_y * 65534)
            if epoch == 4:
                scalars.InsertNextValue(data_x * 65534)
            if epoch == 5:
                scalars.InsertNextValue(data_x * 65534)
            if epoch == 6:
                scalars.InsertNextValue(data_q * 65534)
            if epoch == 7:
                scalars.InsertNextValue(data_q * 65534)
            if epoch == 8:
                scalars.InsertNextValue(data_q * 65534)
            if epoch == 9:
                scalars.InsertNextValue(data_q * 65534)
            if epoch == 10:
                scalars.InsertNextValue(data_q * 65534)
            if epoch == 11:
                scalars.InsertNextValue(data_q * 65534)

        polydata.SetPoints(points)
        polydata.SetDimensions([I, J, 1])
        polydata.GetPointData().SetScalars(scalars)

        DataSetSurfaceFilter = vtk.vtkDataSetSurfaceFilter()
        DataSetSurfaceFilter.SetInputData(polydata)
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
        DataSetMapper.SetScalarRange(0, 65535)
        DataSetMapper.SetLookupTable(LookupTable)
        DataSetMapper.Update()

        Actor = vtk.vtkActor()
        Actor.SetMapper(DataSetMapper)
        Actor.GetProperty().LightingOff()
        Actor.RotateZ(-angle)

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

    return max_x, min_x, max_y, min_y, max_z, min_z, max_q, min_q


def get_heat_conditions(file_name):
    conditions = file_name.split('_')
    A = float(conditions[-1].split('A')[1])
    Ma = float(conditions[-3].split('Ma')[1])
    H = conditions[-4].split('H')[1]
    inlet_name_list = []
    if H == '10km':
        inlet_name_list = [223.252, 26499.9, 0.261534, 0.41351, 0.33756]
    if H == '20km':
        inlet_name_list = [216.65, 5529.31, 0.0545701, 0.0889099, 0.0725796]
    if H == '25km':
        inlet_name_list = [221.552, 2549.22, 0.0251589, 0.0400839, 0.0327216]
    if H == '30km':
        inlet_name_list = [226.509, 1197.03, 0.0118138, 0.0184102, 0.0150287]
    if H == '35km':
        inlet_name_list = [236.513, 574.595, 0.00567081, 0.00846338, 0.00690888]
    if H == '40km':
        inlet_name_list = [250.35, 287.144, 0.00283389, 0.00399568, 0.00326178]
    if H == '45km':
        inlet_name_list = [264.164, 149.101, 0.00147152, 0.00196628, 0.00160513]
    if H == '50km':
        inlet_name_list = [270.65, 79.7791, 0.000787358, 0.00102688, 0.000838268]
    if H == '55km':
        inlet_name_list = [260.771, 42.5251, 0.00041969, 0.000568099, 0.000463755]
    if H == '60km':
        inlet_name_list = [247.021, 21.9587, 0.000216715, 0.000309678, 0.000252798]

    Temperature = inlet_name_list[0]
    Pressure_Pa = inlet_name_list[1]
    Pressure_Atm = inlet_name_list[2]
    Density = inlet_name_list[3]
    Desity_ratio = inlet_name_list[4]

    conditions = []
    conditions.append(A)
    conditions.append(Ma)
    conditions.append(H)
    conditions.append(Temperature)
    conditions.append(Pressure_Pa)
    conditions.append(Pressure_Atm)
    conditions.append(Density)
    conditions.append(Desity_ratio)

    return conditions

def write_filename_to_txt(output_txt_path, file_name):
    f = open(output_txt_path, 'a')
    file_name = file_name + '\n'
    f.write(file_name)
    f.close()


def write_condition_to_txt(output_txt_path1, conditions):
    f = open(output_txt_path1, 'a')
    header = 'A=' + str(conditions[0]) + '\n'
    f.write(header)
    header = 'Ma=' + str(conditions[1]) + '\n'
    f.write(header)
    header = 'H=' + str(conditions[2]) + '\n'
    f.write(header)
    header = 'Temperature=' + str(conditions[3]) + '\n'
    f.write(header)
    header = 'Pressure_Pa=' + str(conditions[4]) + '\n'
    f.write(header)
    header = 'Pressure_Atm=' + str(conditions[5]) + '\n'
    f.write(header)
    header = 'Density=' + str(conditions[6]) + '\n'
    f.write(header)
    header = 'Density_ratio=' + str(conditions[7]) + '\n'
    f.write(header)
    header = 'max_x=' + str(conditions[8]) + '\n'
    f.write(header)
    header = 'min_x=' + str(conditions[9]) + '\n'
    f.write(header)
    header = 'max_y=' + str(conditions[10]) + '\n'
    f.write(header)
    header = 'min_y=' + str(conditions[11]) + '\n'
    f.write(header)
    header = 'max_z=' + str(conditions[12]) + '\n'
    f.write(header)
    header = 'min_z=' + str(conditions[13]) + '\n'
    f.write(header)
    header = 'max_q=' + str(conditions[14]) + '\n'
    f.write(header)
    header = 'min_q=' + str(conditions[15]) + '\n'
    f.write(header)
    f.close()

def master(input_path, output_path, output_txt_path, angle):
    file_name_list = os.listdir(input_path)
    for i, file_name in enumerate(file_name_list):
        input_file = input_path + file_name
        file_name = file_name.split('.hot')[0]
        write_filename_to_txt(output_txt_path, file_name)
        conditions = get_heat_conditions(file_name)

        max_x, min_x, max_y, min_y, max_z, min_z, max_q, min_q = 0, 0, 0, 0, 0, 0, 0, 0

        for epoch in range(12):
            output_file = output_path + file_name
            output_file = output_file + '_' + str(epoch + 1) + '.png'
            max_x, min_x, max_y, min_y, max_z, min_z, max_q, min_q = drawing(input_file, output_file, epoch, angle)
        conditions.append(max_x)
        conditions.append(min_x)
        conditions.append(max_y)
        conditions.append(min_y)
        conditions.append(max_z)
        conditions.append(min_z)
        conditions.append(max_q)
        conditions.append(min_q)
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
    '''
    for i, file_name in enumerate(file_name_list):
        input_file = input_path + file_name
        file_name = file_name.split('.hot')[0]
        write_filename_to_txt(output_txt_path, file_name)
        conditions = get_heat_conditions(file_name)


        max_x, min_x, max_y, min_y, max_z, min_z, max_q, min_q = 0, 0, 0, 0, 0, 0, 0, 0

        for epoch in range(12):
            output_file = output_path + file_name
            output_file = output_file + '_' + str(epoch + 1) + '.png'
            max_x, min_x, max_y, min_y, max_z, min_z, max_q, min_q = drawing(input_file, output_file, epoch, angle)
        conditions.append(max_x)
        conditions.append(min_x)
        conditions.append(max_y)
        conditions.append(min_y)
        conditions.append(max_z)
        conditions.append(min_z)
        conditions.append(max_q)
        conditions.append(min_q)
        print(conditions)
        output_txt_path1 = output_path + file_name + '_' + str(0) + '.txt'
        write_condition_to_txt(output_txt_path1, conditions)
        print("-------数据生成完毕-------")
    print("------全部数据生成完毕-------")
    '''