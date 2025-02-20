from mpi4py import MPI

def main():
    # Ініціалізація MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    # Дані для збору
    data_to_gather = rank + 1
    print(f"Process {rank} sent data: {data_to_gather}")

    # Буфер для отримання даних
    gathered_data = None

    # Збір списку даних на кореневому процесі
    gathered_data = comm.gather(data_to_gather, root=0)

    # Кореневий процес виводить результат
    if rank == 0:
        print(f"Process {rank} gathered data: {gathered_data}")


if __name__ == "__main__":
    main()
