Parallel processing of products on the computer is
facilitated by a variant of (3) for computing $\mathbf {C=AB}$, which is used by standard algorithms (such as in Lapack). In this method, $\mathbf{A}$ is used as given, $\mathbf{B}$ is taken in terms of its column vectors, and the product is computed columnwise; thus,

(5)

Columns of $\mathbf{B}$ are then assigned to different processors (individually or several to each processor), which simultaneously compute the columns of the product matrix $\mathbf{Ab_1,Ab_2}$, etc.

## 7.2 Matrix Multiplication
