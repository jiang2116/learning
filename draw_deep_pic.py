#coding:utf-8
import vtk
from stl import mesh
import numpy as np
import os
#from vtk.util import numpy_support

def my_save_pic(output_file,RenderWindow):
    #对renderwiondow进行保存
    store_renwin = vtk.vtkWindowToImageFilter()
    store_renwin.SetInput(RenderWindow)
    store_renwin.SetScale(1)
    store_renwin.SetInputBufferTypeToRGB()
    store_renwin.ReadFrontBufferOff()
    store_renwin.Update()

    #使用writer写回
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(output_file)
    writer.SetInputData(store_renwin.GetOutput())
    writer.Write()
    #Clean up
    #del store_renwin
    #del writer

def drawing(input_file,output_file):
    #read stl
    #stlreader = vtk.vtkSTLReader()
    #stlreader.SetFileName(input_file)
    #stlreader.Update()
    #stlPolyData=stlreader.GetOutput()
    #print(stlPolyData)

    #read mesh
    your_mesh = mesh.Mesh.from_file(input_file)
    data_array=your_mesh.vectors
    print(data_array.shape)
    
    
    #min/max
    x_min=data_array[:,:,0].min()
    y_min=data_array[:,:,1].min()
    z_min=data_array[:,:,2].min()
    x_range=data_array[:,:,0].max()-data_array[:,:,0].min()
    y_range=data_array[:,:,1].max()-data_array[:,:,1].min()
    z_range=data_array[:,:,2].max()-data_array[:,:,2].min()
    data_array[:,:,0]=(data_array[:,:,0]-x_min)/x_range
    data_array[:,:,1]=(data_array[:,:,1]-y_min)/y_range
    data_array[:,:,2]=(data_array[:,:,2]-z_min)/z_range

    #Poly
    datas={}
    points=vtk.vtkPoints()
    cell_array=vtk.vtkCellArray()
    point_id=0
    for i in range(len(data_array)):
        polygon=vtk.vtkPolygon()
        polygon.GetPointIds().SetNumberOfIds(3)
        for j in range(3):
            if not(data_array[i,j,0],data_array[i,j,1],data_array[i,j,2]) in datas:
                datas[(data_array[i,j,0],data_array[i,j,1],data_array[i,j,2])]=point_id
                points.InsertNextPoint(data_array[i,j,0],data_array[i,j,1],data_array[i,j,2])
                point_id+=1
            polygon.GetPointIds().SetId(j,datas[(data_array[i,j,0],data_array[i,j,1],data_array[i,j,2])])
        cell_array.InsertNextCell(polygon)
    stlPolyData=vtk.vtkPolyData()
    stlPolyData.SetPoints(points)
    stlPolyData.SetPolys(cell_array)



    #权重xyz
    weights=[]
    for i in range(3):
        weight=vtk.vtkDoubleArray()
        for j in range(stlPolyData.GetNumberOfPoints()):
            point_position = stlPolyData.GetPoint(j)
            print(datas[(point_position[0],point_position[1],point_position[2])])
            weight.InsertNextValue(int(point_position[i]*254))
            #print(int(point_position[i]*254))
        weights.append(weight)

    #Filter
    DataSetSurfaceFilter=vtk.vtkDataSetSurfaceFilter()
    DataSetSurfaceFilter.SetInputData(stlPolyData)
    DataSetSurfaceFilter.Update()

    SmoothPolyDataFilter=vtk.vtkSmoothPolyDataFilter()
    SmoothPolyDataFilter.SetNumberOfIterations(60)
    SmoothPolyDataFilter.SetInputConnection(DataSetSurfaceFilter.GetOutputPort())
    SmoothPolyDataFilter.Update()

    PolyDataNormals=vtk.vtkPolyDataNormals()
    PolyDataNormals.SetInputConnection(SmoothPolyDataFilter.GetOutputPort())
    PolyDataNormals.FlipNormalsOn()
    PolyDataNormals.ComputeCellNormalsOn()
    PolyDataNormals.Update()

    #Color
    LookupTable = vtk.vtkLookupTable()
    LookupTable.SetNumberOfTableValues(256)
    LookupTable.Build()
    for i in range(256):
        LookupTable.SetTableValue(i, i/255.0, i/255.0, i/255.0, 1.0)

    #Mapper
    DataSetMapper=vtk.vtkDataSetMapper()
    DataSetMapper.SetInputConnection(PolyDataNormals.GetOutputPort())
    DataSetMapper.SetScalarRange(0,255)
    DataSetMapper.SetLookupTable(LookupTable)
    DataSetMapper.Update()


    Actor = vtk.vtkActor()
    Actor.SetMapper(DataSetMapper)
    Actor.GetProperty().LightingOff()
    #Actor.GetProperty().SetRepresentationToWireframe()
    

    #Renderer
    Renderer = vtk.vtkRenderer()
    Renderer.AddActor(Actor)
    Renderer.SetBackground(1.0, 1.0, 1.0)
    #Renderer.SetBackground(0.9, 0.9, 0.9)

    #Camera
    camera=Renderer.GetActiveCamera()
    camera.ParallelProjectionOn()
    
    #RenderWindow
    RenderWindow = vtk.vtkRenderWindow()
    RenderWindow.AddRenderer(Renderer)
    RenderWindow.SetSize(512, 512)
    RenderWindow.OffScreenRenderingOn()
    RenderWindow.Render()

    #Z+
    Renderer.ResetCamera()
    camera.SetParallelScale(0.5)
    stlPolyData.GetPointData().SetScalars(weights[2])
    DataSetSurfaceFilter.Update()
    my_save_pic(output_file+'1.png',RenderWindow)
    

    #Z-
    Actor.RotateY(180)
    Renderer.ResetCamera()
    camera.SetParallelScale(0.5)
    stlPolyData.GetPointData().SetScalars(weights[2])
    DataSetSurfaceFilter.Update()
    my_save_pic(output_file+'2.png',RenderWindow)
    

    #X+
    Actor.RotateY(270)
    Renderer.ResetCamera()
    camera.SetParallelScale(0.5)
    stlPolyData.GetPointData().SetScalars(weights[0])
    DataSetSurfaceFilter.Update()
    my_save_pic(output_file+'3.png',RenderWindow)
    

    #X-
    Actor.RotateY(180)
    Renderer.ResetCamera()
    camera.SetParallelScale(0.5)
    stlPolyData.GetPointData().SetScalars(weights[0])
    DataSetSurfaceFilter.Update()
    my_save_pic(output_file+'4.png',RenderWindow)
    
    #Y+
    Actor.RotateY(90)
    Actor.RotateX(90)
    Renderer.ResetCamera()
    camera.SetParallelScale(0.5)
    stlPolyData.GetPointData().SetScalars(weights[1])
    DataSetSurfaceFilter.Update()
    my_save_pic(output_file+'5.png',RenderWindow)

    #Y-
    Actor.RotateX(180)
    Renderer.ResetCamera()
    camera.SetParallelScale(0.5)
    stlPolyData.GetPointData().SetScalars(weights[1])
    DataSetSurfaceFilter.Update()
    my_save_pic(output_file+'6.png',RenderWindow)
    
    #stlPolyData.GetPointData().SetScalars(weights[1])
    #DataSetSurfaceFilter.Update()
    
    with open(output_file+'0.txt','w')as f:
        f.write('%0.9f\n%0.9f\n%0.9f\n%0.9f\n%0.9f\n%0.9f'%(x_min,y_min,z_min,x_range,y_range,z_range))

    #Clean up
    del DataSetMapper
    del Actor
    del Renderer
    del RenderWindow

def main():
    #file_path='data/1.blunt_cone'
    #file_path='data/2.double_cone'
    #file_path='data/3.double_ellipsoid'
    file_path='data/4.lifting_body'
    #file_path='data/5.ball_head'

    #with open('C:\\Users\Lenovo\Desktop\jiangtingrui\\result','r')as f:
        #for line in f.readlines():
    drawing('C:\\Users\Lenovo\Desktop\jiangtingrui\\result\\blunt_cone_10_169_10.stl',"C:\\Users\Lenovo\Desktop\jiangtingrui\png\\")

if __name__ == '__main__':
    main()