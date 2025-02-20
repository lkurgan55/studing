from mpi4py import MPI

def test(data, comm):
    rank = comm.Get_rank()
    size = comm.Get_size()
    received_data = bytearray(data)
    partner = (rank + 1) % size

    send_request = comm.Isend(data, dest=partner)
    recv_request = comm.Irecv(received_data, source=partner)

    print(f"Process {rank} send data and waiting for data continues working.")

    MPI.Request.Waitall([send_request, recv_request])

    print(f"""Process {rank} received data {received_data} from process {partner}""")

if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    data_to_exchange = f"Data from process {rank}".encode()

    test(data_to_exchange, comm)
