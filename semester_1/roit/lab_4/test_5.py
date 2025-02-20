from mpi4py import MPI
from time import time

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

def get_and_sum(comm):
    size = comm.Get_size()

    result = 0
    for source in range(1, size):
        received_partial_sum = comm.recv(source=source)
        result += received_partial_sum
    return result

def subsum(comm, data):
    partial_sum = sum([i**(1/i) for i in data])
    comm.send(partial_sum, dest=0) 
    return partial_sum 

if __name__ == "__main__":
    
    input_data = [i for i in range(1, 1234567)]

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    input_data = split_list(input_data, size-1)
    
    if rank == 0:
        start_time = time()
        result = get_and_sum(comm)
        print(f"Main process {rank}: Result Sum = {result}, time spent = {time() - start_time}")
    else:
        data = input_data[rank-1]
        start_time = time()
        result = subsum(comm, data)
        print(f"Process {rank}: Partial Sum = {result}, time spent = {time() - start_time}")
