from mpi4py import MPI

def test(data, comm):
    rank = comm.Get_rank()
    size = comm.Get_size()

    partner = (rank + 1) % size
    received_data = comm.sendrecv(data, dest=partner, source=partner) # Блокуючий обмін даними між процесами

    print(
        f"""
          Process {rank}: Sent data {data} to process {partner},
          Received data '{received_data}' from process {partner}
        """
    )

if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    data_to_exchange = f"Data from process {rank}"

    test(data_to_exchange, comm)
