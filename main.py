import sys
import multiprocessing as mp
import time

from multiprocessing import Process, Value, Lock

def timeit(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        print(f"Час виконання функції {func.__name__}: {time.time() - start_time} секунд")
        return result
    return wrapper

def sum_square_list(numbers: list, final_result = None, lock = None):
    result = 0
    for num in numbers:
        time.sleep(1)
        result += num ** 2
    if final_result is None: return result 
    with lock:
        final_result.value += result

@timeit
def test_one_process(input_list):
    return sum_square_list(input_list)

@timeit
def test_mpi(input_list: list, chunk_size: int):

    final_result = Value('i', 0)
    lock = Lock()
    
    splited_data = [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]

    processes = [Process(target=sum_square_list, args=(data, final_result, lock)) for data in splited_data]

    for p in processes:
        p.start()

    for p in processes:
        p.join()

    return final_result.value

input_data = [
    1, 2, 3, 4, 5, 6, 7, 8, 9,
    1, 2, 3, 4, 5, 6, 7, 8, 9,
    1, 2, 3, 4, 5, 6, 7, 8, 9,
    1, 2, 3, 4, 5, 6, 7, 8, 9,
    1, 2, 3, 4, 5, 6, 7, 8, 9,
]
chunk_size = 3

if __name__ == '__main__':
	print(f"Python версія: {sys.version}, Кількість ядер: {mp.cpu_count()}")

	print(f"Результат 1: {test_one_process(input_data)}")
    
	print(f"Результат 2: {test_mpi(input_data, chunk_size)}")
