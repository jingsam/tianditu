# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import multiprocessing


def check_parallel(check_func, args):
    multiprocessing.freeze_support()
    pool = multiprocessing.Pool()
    cpus = multiprocessing.cpu_count()
    results = []

    for pid in xrange(0, cpus):
        result = pool.apply_async(check_func, args=(args, cpus, pid))
        results.append(result)

    pool.close()
    pool.join()

    errors = []
    for result in results:
        errors.append(result.get())

    return ''.join(errors)
