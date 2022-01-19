import threading, multiprocessing, math

threads_count = multiprocessing.cpu_count()

l=1000000
r=2000000

print(f'Threads: {threads_count}\n')

prime = []

def pierwsza(k):
    s = math.ceil(math.sqrt(k))
    for i in range (2, s+1):
        if k%i == 0:
            return False
    return True

def pierwsza_range(s, e, b, res):
    result = [x for x in range (s, e+1) if pierwsza(x)]
    b.wait()
    res += result

threads_ranges_start = [x for x in range(l, r, math.ceil((r - l)/threads_count))]
threads_ranges_stop = [x - 1 for x in threads_ranges_start[1:]] + [r]

b = threading.Barrier(threads_count)

threads = [threading.Thread(target=pierwsza_range, args=(start, stop, b, prime)) for start, stop in zip(threads_ranges_start, threads_ranges_stop)]

for t in threads:
    t.daemon = True
    t.start()

for t in threads:
    t.join()

print(prime)
print(len(prime))
