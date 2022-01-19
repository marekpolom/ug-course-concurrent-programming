import threading, multiprocessing, time

threads_count = multiprocessing.cpu_count()
lock = threading.Lock()
n = 1000000

print(f'Threads: {threads_count}\n')

suma = 0

def sum_threading(start, end):
    global suma

    for i in range(start, end):
        suma += i

suma_normal = 0

def sum_normal(start, end):
    global suma_normal

    for i in range(start, end):
        suma_normal += i

start = time.time()

for i in range(threads_count):
    [i * int(n/threads_count), n if i ==
     threads_count else i+1 * int(n/threads_count)]

threads = [threading.Thread(target=sum_threading, args=(start, stop)) for start, stop in [
    [i * int(n/threads_count), n if i == threads_count-1 else (i + 1) * int(n/threads_count)] for i in range(threads_count)]]

for t in threads:
    t.daemon = True
    t.start()

for t in threads:
    t.join()

end = time.time()

print(f'Threading | Time: {end - start} | Sum: {suma}')

start = time.time()
sum_normal(0, n)
end = time.time()

print(f'No threading | Time: {end - start} | Sum: {suma_normal}')
