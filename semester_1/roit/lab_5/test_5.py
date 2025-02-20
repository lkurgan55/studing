from mpi4py import MPI
from time import time
import random

def split_list_randomly(input_list, n):
    # Випадковим чином вибираємо розмір кожної частини
    sizes = [random.randint(1, len(input_list)) for _ in range(n)]

    # Забезпечуємо, щоб сума розмірів не перевищувала загальний розмір списку
    while sum(sizes) > len(input_list):
        sizes[random.randint(0, n - 1)] -= 1

    # Розбиваємо список на частини згідно з розмірами
    result = [input_list[sum(sizes[:i]):sum(sizes[:i+1])] for i in range(n)]

    return result


def subsum(data):
    return sum([(i**(1/i))**2 for i in data])

if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if rank == 0:
        input_data = split_list_randomly([i for i in range(1, 12345678)], size)
        root_start_time = time()
    else:
        input_data = []
    
    n = comm.bcast(len(input_data), root=0) # розсилка усім процесам про кількість списків даних
    input_data = comm.scatter(input_data, root=0) # отримання частини даних
    proccess_start_time = time()
    calculated_data = subsum(input_data) # обчилення
    result_time = time()
    total_sum = comm.reduce(calculated_data, MPI.SUM, root=0) # знаходження суми результатів
    # збір статистики роботи процесів
    result = comm.gather((rank, len(input_data), result_time - proccess_start_time), root=0)
    
    print(f"Process {rank}: SubSum = {calculated_data}")
    if rank == 0:
        print(f"\nProcces {rank} total sum = {total_sum}, total time = {time() - root_start_time}\n")
        print("Stats:")
        for r, l, t in result:
            print(f"  Procces {r} calculated {l} of numbers, spent time = {t}")
