from mpi4py import MPI

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    send_data = f"Hello from process {rank}"

    # Буфер для отримання даних
    recv_data = None

    # Широкомовний обмін даними
    recv_data = comm.bcast(send_data, root=0)

    # Виведення результатів
    print(f"Process {rank} received: {recv_data}")

if __name__ == "__main__":
    main()
