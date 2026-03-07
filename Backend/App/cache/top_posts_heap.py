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
        self.max_size = max_size
        self.update_intervall = update_intervall
        self.post_lookup = {} # {post_id: heap_index}
        
    async def update_heap_tracker(self):
        while True:
            asyncio.sleep(self.update_intervall)

    def heapify_down(self, cur_i: int):
        smallest = cur_i
        len_arr = len(self.arr)
        while True:
            smallest = cur_i
            # calculating left and right index
            left = 2 * cur_i + 1
            right = 2 * cur_i + 2

            # setting smallest if left or right exists
            if left < len_arr and self.arr[left][1] < self.arr[smallest][1]: smallest = left
            if right < len_arr and self.arr[right][1] < self.arr[smallest][1]: smallest = right

            # swapping values if a new smallest occured
            if smallest == cur_i: return
            self.arr[cur_i], self.arr[smallest] = self.arr[smallest], self.arr[cur_i]

            # updating values in post_lookup
            self.post_lookup[self.arr[cur_i][0]] = cur_i
            self.post_lookup[self.arr[smallest][0]] = smallest

            cur_i = smallest

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
            if parent_i < 0 or self.arr[parent_i][1] <= self.arr[cur_i][1]: return cur_i # no swapping

            # swapping parent with child
            self.arr[cur_i], self.arr[parent_i] = self.arr[parent_i], self.arr[cur_i]

            # updating values in post_lookup
            self.post_lookup[self.arr[cur_i][0]] = cur_i
            self.post_lookup[self.arr[parent_i][0]] = parent_i
            
            cur_i = parent_i

    def insert(self, item: tuple[int, int]):
        """Function to insert tuple[post_id, hotness]"""

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
            self.heapify_up(self, cur_i)

    def remove_from_heap(self, post_id: int):
        index = self.post_lookup.pop(post_id, None)
        if index == None: return # item doesn't exist

        # updating heap
        last_item = self.arr.pop()
        
        self.arr[index] = last_item # removes item
        self.post_lookup[last_item[0]] = index

        if index == len(self.arr) - 1: return # nothing to update

        parent_i = (index - 1) // 2
        if self.arr[parent_i][1] > last_item[1]: self.heapify_up(index)
        else: self.heapify_down(index)

    def return_all() -> list[tuple[int, int]]:
        """Returns the top n hottest post"""