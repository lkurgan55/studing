from mpi4py import MPI

def main():
    # Ініціалізація MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    # Дані для обміну
    send_data = rank + 1

    # Буфер для отримання результату reduce
    result = None
    print(f"Process {rank} send data: {send_data}")
    result = comm.reduce(send_data, op=MPI.SUM, root=0)

    if rank == 0:
        print(f"Process {rank} reduced result: {result}")

if __name__ == "__main__":
    main()
