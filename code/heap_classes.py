from numpy import ndarray, full

# Class to define a min heap and its operations for priority queue implementation for efficient pathfinding

class Heap:

    def __init__(self, array: ndarray) -> None:

        # Here we are converting an array data structure to a heap
        self.heap = array

        self.root = 0
        self.free_child = 0

    # Procedure to insert an item into the min heap priority queue

    def insert(self, GridSquare: object) -> None:

        # First we add the item to the last element in the list (next available child node)
        self.heap[self.free_child] = GridSquare

        # Now we will need to place the child in the correct position based on its priority (i.e. smallest f cost)
        current_node = self.free_child
        parent_node = (current_node - 1) // 2

        while current_node != self.root and self.heap[current_node].f_cost < self.heap[parent_node].f_cost:

            # Swap the parent and the child node
            self.heap[parent_node], self.heap[current_node] = self.heap[current_node], self.heap[parent_node]

            current_node = parent_node
            parent_node = (current_node - 1) // 2

        # Update the position of the next free child - next available free index
        self.free_child += 1

    # Function to return the smallest element in the min heap priority queue

    def extract(self) -> object:

        item_to_extract = self.heap[self.root]

        # If the heap is empty, then return an error
        if item_to_extract is None:

            print("Error - heap is empty")
            return None

        # First we move the last child node to replace the root
        self.heap[self.root], self.heap[self.free_child - 1] = self.heap[self.free_child - 1], None
        
        # Update the free child pointer
        self.free_child -= 1

        # Now, in order to preserve the min heap property, we need to fix the root node
        # Therefore we need to perform a reheapify operation
        current_parent_node = self.root

        # While the current node has children, replace the parent with the smallest child node
        left_child = current_parent_node * 2 + 1
        right_child = current_parent_node * 2 + 2

        while self.heap[left_child] is not None or self.heap[right_child] is not None:

            min_child_node = None

            if self.heap[left_child] is None:

                min_child_node = right_child

            elif self.heap[right_child] is None:

                min_child_node = left_child

            else:

                if self.heap[left_child].f_cost < self.heap[right_child].f_cost:

                    min_child_node = left_child

                else:

                    min_child_node = right_child

            # If the smallest child node is less than the parent, swap the child and the parent to conserve the min heap property
            if self.heap[min_child_node].f_cost < self.heap[current_parent_node].f_cost:

                self.heap[min_child_node], self.heap[current_parent_node] = self.heap[current_parent_node], self.heap[min_child_node]

            # Move to the next index in the array - the loop will end once the first leaf node is reached as all proceeding nodes will
            # also be leaf nodes
            current_parent_node += 1
            left_child = current_parent_node * 2 + 1
            right_child = current_parent_node * 2 + 2

        return item_to_extract



        
# Testing

if __name__ == "__main__":

    # Instantiate the heap object
    Example_Heap = Heap(full(9, None))    # Heap of size 10

    for i in range(7):

        # Create a new node and insert it into the min heap priority queue
        number = int(input("Number to insert: "))
        Example_Heap.insert(number)


    print(Example_Heap.heap)

    min_value = 0

    while min_value is not None:

        min_value = Example_Heap.extract()
        print(min_value)


    print("Main File Executing")



