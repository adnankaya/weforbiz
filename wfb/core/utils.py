from django.db import connection, reset_queries
import functools
import time
from django.utils import timezone


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_today_with_timezone():
    today = timezone.make_aware(
        timezone.datetime.today(),
        timezone.get_default_timezone()
    )
    return today


def query_debugger(func):

    @functools.wraps(func)
    def inner_func(*args, **kwargs):
        reset_queries()

        start_queries = len(connection.queries)

        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        end_queries = len(connection.queries)
        # TODO remove
        # print(connection.queries)
        print('='*100)
        print(f"Function : {func.__qualname__}")
        print(f"Number of Queries : {end_queries - start_queries}")
        print(f"Finished in : {(end - start):.4f}s")
        print('='*100)
        return result

    return inner_func
