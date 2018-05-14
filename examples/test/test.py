from multiprocessing.pool import ThreadPool
from multiprocessing import Pool
import threading
import time
import requests


def hh(i=0):
    time.sleep(1)
    # requests.get('https://baidu.com')

# start_time = time.time()
# threads = []
# for i in range(200):
#     t = threading.Thread(target=hh)
#     threads.append(t)
#     t.start()
#
# for t in threads:
#     t.join()
# print(time.time() - start_time)
del None
start_time = time.time()
pool = ThreadPool(15)
pool.map(lambda x: x, range(15))
time.sleep(1)
start_time = time.time()
for i in range(200):
    pool.apply_async(hh)

pool.close()
pool.join()

print(time.time() - start_time)


