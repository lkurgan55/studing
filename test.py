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

# Приклад використання
my_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
num_parts = 6

result = split_list(my_list, num_parts)
print(result)
