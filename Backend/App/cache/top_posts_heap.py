# Top-N-Heap that stores the top hottest post_ids
from datetime import datetime
from collections import deque
import asyncio
def calculate_hotness(votes: int, created_at: datetime):
    """
    Function that calculates the hotness of a post\n
    votes has to be a sum of all (downvotes & upvotes)
    """
    ...

class TopNHeap():
    def __init__(self, arr: list[tuple[int, int]], max_size: int, update_intervall: int):
        """
        Top-N-Heap for the top n hottest post in memory\n
        arr must be a list of tuples with [0] = post_id and [1] = hotness
        """
        self.arr = arr
        self.sorted_cache = None
        self.max_size = max_size
        self.update_intervall = update_intervall
    async def update_heap_tracker(self):
        while True:
            asyncio.sleep(self.update_intervall)

    def heapify_down(self, cur_i: int):
        smallest = cur_i
        len_arr = len(self.arr)
        while True:
            prev_smallest = smallest
            # calculating left and right index
            left = 2 * cur_i + 1
            right = 2 * cur_i + 2

            # setting smallest if left or right exists
            if left < len_arr and self.arr[left][1] < self.arr[smallest][1]: smallest = self.arr[left][1]
            if right < len_arr and self.arr[right][1] < self.arr[smallest][1]: smallest = self.arr[right][1]

            # swapping values if a new smallest occured
            if smallest == prev_smallest: return
            self.arr[prev_smallest], self.arr[smallest] = self.arr[smallest], self.arr[prev_smallest]

    def build_max_heap(self):
        # getting index of last element with a child
        cur_i = (len(self.arr) - 2) // 2
        
        for cur_i in range(cur_i, -1, -1):
            self.heapify_down(cur_i)
    
    def peak(self) -> tuple[int, int]:
        """Returns tuple with the unhottest post in the array"""
        return self.arr[0]
    
    def heapify_up(self, cur_i):
        while True:
            parent_i = (cur_i - 1) // 2
            if self.arr[parent_i][1] <= self.arr[cur_i][1] or parent_i < 0: return
            # swapping parent with child
            self.arr[cur_i], self.arr[parent_i] = self.arr[parent_i], self.arr[cur_i]
            cur_i = parent_i

    def insert(self, item: tuple[int, int]):
        """Function to insert tuple[post_id, hotness]"""
        if item[1] <= self.arr[0]: return # returning if hotness is too small
        self.arr.append(item)
        self.sorted_cache = None # removing stored arr

        # checking if the array is full
        if self.max_size <= len(self.arr):
            self.arr[-1], self.arr[0] = self.arr[0], self.arr[-1]
            self.heapify_down(0)
        else:
            cur_i = len(self.arr) - 1
            self.heapify_up(self, cur_i)

    def return_all() -> list[tuple[int, int]]:
        """Returns the top n hottest post"""