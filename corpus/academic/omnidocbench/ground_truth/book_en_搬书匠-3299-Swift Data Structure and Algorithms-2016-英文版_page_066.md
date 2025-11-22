# Implementing subscripting

Subscripts can be defined for classes, structures, and enumerations. They are used to provide a shortcut to elements in collections, lists, and sequence types by allowing terser  syntax. They can be used to set and get elements by specifying an index instead of using separate methods to set or retrieve values.

# Subscript syntax

You can define a subscript that accepts one or more input parameters, the parameters can be of different types, and their return value can be of any type. Use the subscript keyword to define a subscript, which can be defined as read-only, or provide a getter and setter to access elements:

class MovieList {\n\tprivate var tracks = ["The Godfather", "The Dark Knight", "Pulp Fiction"]\n\tsubscript(index: Int) -> String {\n\t\tget {\n\t\t\treturn self.tracks[index]\n\t\t}\n\t\tset {\n\t\t\tself.tracks[index] = newValue\n\t\t}\n\t}\n}\nvar movieList = MovieList()\nvar aMovie = movieList[0]\n// The Godfather\nmovieList[1] = "Forest Gump"\naMovie = movieList[1]\n// Forest Gump

# Subscript options

Classes and structures can return as many subscript implementations as needed. The  support for multiple subscripts is known as subscript overloading, the correct subscript to be used will be inferred based on the subscript value types.

## Working with Commonly Used Data Structures
