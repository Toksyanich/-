def func(mass):
    temp_number = []
    min_number = len(mass[0])
    for i in range(len(mass)):
        if min_number > len(mass[i]):
            min_number = len(mass[i])
    ji = -1
    for j in range(min_number):
        for i in range(len(mass)):
            if (i == 0):
                temp_number.append(mass[i][j])
                ji += 1
            elif temp_number[ji] == mass[i][j]:
                print('ravno')
            else:
                temp_number.pop()
                ji -= 1
    return temp_number


input_str = input().strip()

if input_str.startswith('['):
    input_str = input_str[1:-1]
    if input_str:
        mass = [s.strip('"\'') for s in input_str.split(',')]
    else:
        mass = []
else:
    mass = input_str.split()


if mass:
    res = ''.join(func(mass))
    print(f'{res}')
else:
    print('')
