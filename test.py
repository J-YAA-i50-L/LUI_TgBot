def full(array):
    array1 = array
    for i in range(len(array1)):
        array1[i] = 1


array = [0, 0, 0]

full(array)
print(str(array).replace('[', '').replace(']', ''))
