from time import time
from multiprocessing import Pool, cpu_count


def get_num(n):    
    result = []
    for i in range(1, n+1):
        if n % i == 0:
            result.append(i)
    return result


def factorize(*numbers):
    return [get_num(number) for number in numbers]


def factorize_pr(*numbers):
    with Pool(processes=cpu_count()) as pool:
        result = pool.map(get_num, numbers)
    return result


if __name__ == "__main__":
    start_time = time()
    a, b, c, d  = factorize(128, 255, 99999, 10651060)
    print(f'Sync time: {time() - start_time}')

    start_time_pr = time()
    a, b, c, d  = factorize_pr(128, 255, 99999, 10651060)
    print(f'Process time: {time() - start_time_pr}')    

    assert a == [1, 2, 4, 8, 16, 32, 64, 128]
    assert b == [1, 3, 5, 15, 17, 51, 85, 255]
    assert c == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
    assert d == [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079, 152158, 304316, 380395, 532553, 760790, 1065106, 1521580, 2130212, 2662765, 5325530, 10651060]

    