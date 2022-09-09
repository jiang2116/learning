import numpy as np

def get_data_matrix(data_matrix_zone, topo_relation):
    matrix = []
    for i, topo in enumerate(topo_relation):
        row = []
        for j, index in enumerate(topo):
            point_message = data_matrix_zone[index - 1, :]
            row.append(point_message)
        matrix.append(row)
    matrix = np.array(matrix)

    return matrix

def read_3D_flow_field_data(filename):#这个函数是读取3D流场的，读取2D流场和这个几乎一样的
    x_max = -1000000000000000
    x_min = 1000000000000000
    y_max = -1000000000000000
    y_min = 1000000000000000
    z_max = -1000000000000000
    z_min = 1000000000000000
    q_max = -1000000000000000
    q_min = 1000000000000000#极值计算

    data_matrix=[] #n*3*3
    data_matrix_zone = []
    topo_relation = []
    with open(filename) as file:
        lines=file.readlines()
        for i,line in enumerate(lines):
            if(i < 2):
                continue
            line = line.replace('\n','').lower()
            variable = line.split(' ')
            if(variable[0] == 'zone'):
                if len(data_matrix_zone) == 0:
                    continue

                data_matrix_zone = np.array(data_matrix_zone)
                topo_relation = np.array(topo_relation)
                topo_relation = topo_relation[:, 0:3]
                data_matrix.append(get_data_matrix(data_matrix_zone, topo_relation))
                data_matrix_zone = []
                topo_relation = []
                continue
            if(variable[0] == 'n'):
                continue
            if(variable[0] == 'e'):
                continue
            if(variable[0] == 'et'):
                continue
            if(variable[0] == 'f'):
                continue
            if(len(variable) <= 9):
                if(len(variable) <= 8):
                    continue
                values = []
                for j, value in enumerate(variable):
                    if value == '':
                        continue
                    values.append(int(value))
                topo_relation.append(values)
            else:
                values = []
                index = -1
                for j, value in enumerate(variable):
                    if value == '':
                        continue
                    index += 1
                    values.append(np.double(value))
                    #取到最大值和最小值
                    if index == 0:
                        x_max = max(x_max, np.double(value))
                        x_min = min(x_min, np.double(value))
                        continue
                    if index == 1:
                        y_max = max(y_max, np.double(value))
                        y_min = min(y_min, np.double(value))
                    if index == 2:
                        z_max = max(z_max, np.double(value))
                        z_min = min(z_min, np.double(value))
                    if index == 7:
                        q_max = max(q_max, np.double(value))
                        q_min = min(q_min, np.double(value))
                data_matrix_zone.append(values)
        #对最后一个块进行处理
        data_matrix_zone = np.array(data_matrix_zone)
        topo_relation = np.array(topo_relation)
        topo_relation = topo_relation[:, 0:3]
        data_matrix.append(get_data_matrix(data_matrix_zone, topo_relation))

        return data_matrix, x_max, x_min, y_max, y_min, z_max, z_min, q_max, q_min


if __name__ == '__main__':
    input_path = r'C:\Users\Lenovo\Desktop\jjjjj\新建文件夹\TBCC_H25km_Ma3_A5_T850.tec'
    data_matrix, x_max, x_min, y_max, y_min, z_max, z_min, q_max, q_min = read_3D_flow_field_data(input_path)
    print(x_max, x_min, y_max, y_min, z_max, z_min, q_max, q_min)
    for i, matrix in enumerate(data_matrix):
        print(matrix.shape)