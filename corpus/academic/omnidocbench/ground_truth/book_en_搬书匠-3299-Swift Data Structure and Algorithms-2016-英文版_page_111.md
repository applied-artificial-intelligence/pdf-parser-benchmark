The sink and swim methods were inspired by the book Algorithms by Sedgewick and Wayne, Fourth Edition, Section 2.4.

The structure accepts any type that conforms to the Comparable protocol. The single initializer allows you to optionally specify the sorting order and a list of starting values. The default sorting order is descending and the default starting values are an empty collection:

"/// Initialization\nvar priorityQueue = PriorityQueue<String>(ascending: true)\n/// Initializing with starting values\npriorityQueue = PriorityQueue<String>(ascending: true, startingValues: ["Coldplay", "OneRepublic", "Maroon 5", "Imagine Dragons", "The Script"])\n\nvar x = priorityQueue.pop()\n/// Coldplay\nx = priorityQueue.pop()\n/// Imagine Dragons"

# Protocols

The PriorityQueue conforms to sequence, collection, and IteratorProtocol, so you can treat it like any other Swift sequence and collection:

"extension PriorityQueue: IteratorProtocol {\n\tpublic typealias Element = T\n\tmutating public func next() -> Element? { return pop() }\n}\nextension PriorityQueue: Sequence {\n\tpublic typealias Iterator = PriorityQueue\n\tpublic func makeIterator() -> Iterator { return self }\n}"

This allows you to use Swift standard library functions on a PriorityQueue and iterate through a PriorityQueue like this:

"for x in priorityQueue {\n\tprint(x)\n}\n// Coldplay"

## Standing on the Shoulders of Giants
