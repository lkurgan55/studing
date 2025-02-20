from mpi4py import MPI
from time import time


def calculate_position(list_A, list_B, position):
    result = 0
    for element_a, element_b in zip(list_A, list_B):
        result += element_a * element_b
    return result, position

def zip_matix(matrix_A, matrix_B):
    # Транспонування матриці
    matrix_B_T = [[matrix_B[j][i] for j in range(len(matrix_B))] for i in range( len(matrix_B[0]))]

    result = []
    row_index = -1
    col_index = -1

    for row in matrix_A:
        row_index += 1
        col_index = -1
        for col in matrix_B_T:
            col_index += 1
            result.append([(row, col), (row_index, col_index)])

    return result

def split_list(lst, N):
    avg = len(lst) // N
    remainder = len(lst) % N

    result = []
    start = 0

    for i in range(N):
        end = start + avg + (1 if i < remainder else 0)
        result.append(lst[start:end])
        start = end

    return result

def create_matrix(data, size):
    result = []
    for _ in range(size[0]):
        result.append([0]*size[1])
    for element, position in data:
        result[position[0]][position[1]] = element
    return result


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    start_time = time()
    from test_case_2 import matrix_A, matrix_B
    data = zip_matix(matrix_A, matrix_B)
    data_list = split_list(data, size-1)
    for i in range(1, size):
        comm.send(data_list[i-1], dest=i, tag=i)
else:
    data_list = comm.recv(source=0)
    #print(f"Processor {rank} recived {data_list}")
    result = []
    for data in data_list:
        result.append(calculate_position(data[0][0], data[0][1], data[1]))
    #print(f"Processor {rank} proces values {result}")
    data = result


all_result = comm.gather(data, root=0) # збір результатів з процесів
if rank == 0:
    result = []
    for subresult in all_result:
        result += subresult

    result = create_matrix(result, (len(matrix_A[0]), len(matrix_B)))
    print(f"\nSpent Time: {time() - start_time}")
    # print("\nResult Matrix:")

    # for row in result:
    #     print(row)

    # print()
