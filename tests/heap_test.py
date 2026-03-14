from Backend.App.cache.hotness_calc import calculate_hotness
from Backend.App.cache.top_posts_heap import TopNHeap
from datetime import datetime
arr = [
    (1, calculate_hotness(120, datetime(2026, 3, 7, 9, 0)),  datetime(2026, 3, 7, 9, 0), 120),
    (2, calculate_hotness(95,  datetime(2026, 3, 7, 9, 5)),  datetime(2026, 3, 7, 9, 5), 95),
    (3, calculate_hotness(60,  datetime(2026, 3, 7, 9, 10)), datetime(2026, 3, 7, 9, 10), 60),
    (4, calculate_hotness(42,  datetime(2026, 3, 7, 9, 15)), datetime(2026, 3, 7, 9, 15), 42),
    (5, calculate_hotness(30,  datetime(2026, 3, 7, 9, 20)), datetime(2026, 3, 7, 9, 20), 30),
    (6, calculate_hotness(25,  datetime(2026, 3, 7, 9, 25)), datetime(2026, 3, 7, 9, 25), 25),
    (7, calculate_hotness(19,  datetime(2026, 3, 7, 9, 30)), datetime(2026, 3, 7, 9, 30), 19),
    (8, calculate_hotness(15,  datetime(2026, 3, 7, 9, 35)), datetime(2026, 3, 7, 9, 35), 15),
    (9, calculate_hotness(12,  datetime(2026, 3, 7, 9, 40)), datetime(2026, 3, 7, 9, 40), 12),
    (10, calculate_hotness(10, datetime(2026, 3, 7, 9, 45)), datetime(2026, 3, 7, 9, 45), 10),
    (11, calculate_hotness(8,  datetime(2026, 3, 7, 9, 50)), datetime(2026, 3, 7, 9, 50), 8),
    (12, calculate_hotness(7,  datetime(2026, 3, 7, 9, 55)), datetime(2026, 3, 7, 9, 55), 7),
    (13, calculate_hotness(6,  datetime(2026, 3, 7, 10, 0)), datetime(2026, 3, 7, 10, 0), 6),
    (14, calculate_hotness(5,  datetime(2026, 3, 7, 10, 5)), datetime(2026, 3, 7, 10, 5), 5),
    (15, calculate_hotness(4,  datetime(2026, 3, 7, 10, 10)),datetime(2026, 3, 7, 10, 10), 4),
    (16, calculate_hotness(3,  datetime(2026, 3, 7, 10, 15)),datetime(2026, 3, 7, 10, 15), 3),
    (17, calculate_hotness(3,  datetime(2026, 3, 7, 10, 20)),datetime(2026, 3, 7, 10, 20), 3),
    (18, calculate_hotness(2,  datetime(2026, 3, 7, 10, 25)),datetime(2026, 3, 7, 10, 25), 2),
    (19, calculate_hotness(2,  datetime(2026, 3, 7, 10, 30)),datetime(2026, 3, 7, 10, 30), 2),
    (20, calculate_hotness(1,  datetime(2026, 3, 7, 10, 35)),datetime(2026, 3, 7, 10, 35), 1),
    (21, calculate_hotness(1,  datetime(2026, 3, 7, 10, 40)),datetime(2026, 3, 7, 10, 40), 1),
    (22, calculate_hotness(0,  datetime(2026, 3, 7, 10, 45)),datetime(2026, 3, 7, 10, 45), 0),
    (23, calculate_hotness(-2, datetime(2026, 3, 7, 10, 50)),datetime(2026, 3, 7, 10, 50), -2),
    (24, calculate_hotness(-5, datetime(2026, 3, 7, 10, 55)),datetime(2026, 3, 7, 10, 55), -5),
]
h = TopNHeap(arr, 25, 12)
def print_sorted():
    for r in h.return_all(): print(r[1])

def print_heap():
    for r in h.arr: print(r[0], ":", r[1])

def is_heap() -> bool:
    len_arr = len(h.arr)

    for i, r in enumerate(h.arr):
        left = 2 * i + 1
        right = 2 * i + 2

        if left < len_arr:
            if h.arr[left][1] < r[1]:
                print(f"Err i: {i}")
                return False

        if right < len_arr:
            if h.arr[right][1] < r[1]:
                print(f"Err i: {i}")
                return False

    return True
    
h.build_min_heap()
h.insert((25, calculate_hotness(100,  datetime(2026, 3, 7, 10, 45)), datetime(2026, 3, 7, 10, 45), 4))
arr_before = h.arr
# print_sorted()
if h.arr != arr_before: print("Sorting changed original heap")
print(is_heap())
print_sorted()

