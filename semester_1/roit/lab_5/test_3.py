from mpi4py import MPI

def main():
    # Ініціалізація MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    data_to_scatter = None

    # Кореневий процес ініціалізує дані
    if rank == 0:
        data_to_scatter = [i for i in range(comm.Get_size())]
        print(f"Data on process {rank}: {data_to_scatter}")

    # Буфер для отримання даних
    received_data = None

    # Розсилка списку даних
    received_data = comm.scatter(data_to_scatter, root=0)

    print(f"Process {rank} received: {received_data}")

if __name__ == "__main__":
    main()
