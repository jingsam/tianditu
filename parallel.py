# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import multiprocessing


def check_parallel(check_func, in_fc, tolerance):
    multiprocessing.freeze_support()
    pool = multiprocessing.Pool()
    cpus = multiprocessing.cpu_count()
    results = []

    for pid in xrange(0, cpus):
        result = pool.apply_async(check_func, args=(in_fc, tolerance, cpus, pid))
        results.append(result)

    pool.close()
    pool.join()

    errors = []
    for result in results:
        errors.append(result.get())

    return ''.join(errors)
