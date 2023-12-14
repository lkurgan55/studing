from mpi4py import MPI

def ring_exchange(data, comm):
    rank = comm.Get_rank()
    size = comm.Get_size()

    destination = (rank + 1) % size
    source = (rank - 1 + size) % size

    received_data = comm.sendrecv(data, dest=destination, source=source)
    print(
        f"""
          Process {rank}: Sent data {data} to process {destination},
          Received data '{received_data}' from process {source}
        """
    )

if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    data_to_exchange = [rank, rank + 1, rank + 2]

    ring_exchange(data_to_exchange, comm)
