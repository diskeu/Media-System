# Top-N-Heap that stores the top hottest post_ids
from datetime import datetime
from Backend.App.cache.hotness_calc import calculate_hotness
import asyncio

class TopNHeap():
    def __init__(self, arr: list[tuple[int, int, datetime, int]], max_size: int, update_intervall: int):
        """
        Top-N-Heap for the top n hottest post in memory\n
        arr must be a list of tuples with [0] = post_id, [1] = hotness and [2] = created_at, i[3] = net_votes
        """
        self.arr = arr
        self.max_size = max_size
        self.update_intervall = update_intervall
        self.post_lookup = {} # {post_id: heap_index}
        self.cache: list | None = arr
        
    async def update_heap_tracker(self):
        while True:
            await asyncio.sleep(self.update_intervall)
            self.cache = None
            # updating all values of the old heap
            for i in range(len(self.arr)):
                hotness = calculate_hotness(self.arr[i][3], self.arr[1][2])
                self.arr[i] = (self.arr[i][0], hotness, self.arr[i][2], self.arr[i][3])
            self.update_all()
                        
    def heapify_down(self, cur_i: int, arr: list = None, len_arr: int = None):
        smallest = cur_i
        # flag
        new_arr: bool = True if arr != None else False

        # if prefixed vals
        if not arr: arr = self.arr
        if not len_arr: len_arr = len(arr)

        while True:
            smallest = cur_i
            # calculating left and right index
            left = 2 * cur_i + 1
            right = 2 * cur_i + 2

            # setting smallest if left or right exists
            if left < len_arr and arr[left][1] < arr[smallest][1]: smallest = left
            if right < len_arr and arr[right][1] < arr[smallest][1]: smallest = right

            # swapping values if a new smallest occured
            if smallest == cur_i: return
            arr[cur_i], arr[smallest] = arr[smallest], arr[cur_i]

            # updating values in post_lookup
            if new_arr:
                self.post_lookup[arr[cur_i][0]] = cur_i
                self.post_lookup[arr[smallest][0]] = smallest

            cur_i = smallest

    def update_all(self):
        self.cache = None
        # getting index of last element with a child
        cur_i = (len(self.arr) - 2) // 2
        
        for cur_i in range(cur_i, -1, -1):
            self.heapify_down(cur_i)
        
    def build_min_heap(self):
        """Wrapper for update_all to build completly new min - heap"""
        # creating post_lookup
        self.post_lookup = {post_id: i for i, (post_id, _, _, _) in enumerate(self.arr)}

        self.update_all()
    
    def peak(self) -> tuple[int, int, datetime, int]:
        """Returns tuple with the unhottest post in the array"""
        return self.arr[0]
    
    def heapify_up(self, cur_i):
        while True:
            parent_i = (cur_i - 1) // 2
            if parent_i < 0 or self.arr[parent_i][1] <= self.arr[cur_i][1]: return cur_i # no swapping

            # swapping parent with child
            self.arr[cur_i], self.arr[parent_i] = self.arr[parent_i], self.arr[cur_i]

            # updating values in post_lookup
            self.post_lookup[self.arr[cur_i][0]] = cur_i
            self.post_lookup[self.arr[parent_i][0]] = parent_i
            
            cur_i = parent_i

    def insert(self, item: tuple[int, int, datetime, int]):
        """Function to insert tuple[post_id, hotness, created_at, net_votes]"""
        self.cache = None
        
        # checking if the array is full
        if self.max_size <= len(self.arr):
            if item[1] <= self.arr[0][1]: return # returning if hotness is too small

            # removing old item
            self.post_lookup.pop(self.arr[0][0])

            self.arr[0] = item                   # removing unhottest item
            self.post_lookup[item[0]] = 0        # item is now on top of the arr

            self.heapify_down(0)
        else:
            self.arr.append(item)
            cur_i = len(self.arr) - 1
            self.post_lookup[item[0]] = cur_i
            self.heapify_up(cur_i)

    def remove_from_heap(self, post_id: int):
        self.cache = None

        index = self.post_lookup.pop(post_id, None)
        if index == None: return # item doesn't exist

        # updating heap
        last_item = self.arr.pop()
        
        self.arr[index] = last_item # removes item
        self.post_lookup[last_item[0]] = index

        if index == len(self.arr) - 1: return # nothing to update

        # Rebalance Heap
        parent_i = (index - 1) // 2
        if index == 0 or self.arr[parent_i][1] < last_item[1]: self.heapify_down(index)
        else: self.heapify_up(index)

    def update_hotness(self, post_id: int, hotness: int): # T: O(log2(size arr))
        self.cache = None

        heap_i = self.post_lookup.get(post_id, None)
        if heap_i == None: return

        self.arr[heap_i][1] = hotness

        # Rebalance Heap
        parent_i = (heap_i - 1) // 2
        if heap_i == 0 or self.arr[parent_i][1] < hotness: self.heapify_down(heap_i)
        else: self.heapify_up(heap_i)

    def heap_sort(self, arr: list): # T: O(n * log(n)), S: O(1)
        for i in range(len(arr) - 1, 0, -1):
            arr[0], arr[i] = arr[i], arr[0]
            self.heapify_down(0, arr, i)
        return arr

    def return_all(self) -> list[tuple[int, int, datetime]]:
        """Returns the top n hottest post from max -> min"""
        if self.cache: return self.cache
        arr = self.heap_sort(self.arr.copy())
        self.cache = arr
        return arr
    
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
h.build_min_heap()
h.insert((25, calculate_hotness(100,  datetime(2026, 3, 7, 10, 45)), datetime(2026, 3, 7, 10, 45), 4))
for r in h.return_all():
    print(r[1])