tiating and taking square roots,

using the fact that $1 < e < 3$.

B-3 View $x_1,\ldots,x_n$ as an arrangement of the numbers
$1,2,\ldots,n$ on a circle. We prove that the optimal arrangement is

To show this, note that if ${ a, b }$ is a pair of adjacent numbers and $c, d$ is another pair (read in the same order around the circle) with $a < d$ and $b > c$, then the segment from $b$ to $c$ can be reversed, increasing the sum by

Now relabel the numbers so they appear in order as follows:

where without loss of generality we assume $a_{n-1} > a_{n-2}$. By considering the pairs $a_{n-2}, a_n$ and $a_{n-1}, a_{n-3}$ and using the trivial fact $a_n > a_{n-1}$, we deduce $a_{n-2} > a_{n-3}$. We then compare the pairs $a_{n-4}, a_{n-2}$ and $a_{n-1}, a_{n-3}$, and using that $a_{n-1} > a_{n-2}$, we deduce $a_{n-3} > a_{n-4}$. Continuing in this fashion, we prove that $a_n > a_{n-1} > \cdots > a_1$ and so $a_k = k$ for $k=1,2,\dots,n$, i.e. that the optimal arrangement is as claimed. In particular, the maximum value of the sum is

Alternate solution: We prove by induction that the value given above is an upper bound; it is clearly a lower bound because of the arrangement given above. Assume this is the case for $n-1$. The optimal arrangement for $n$ is obtained from some arrangement for $n-1$ by inserting $n$ between some pair $x,y$ of adjacent terms. This operation increases the sum by $nx+ny-xy = n^2 - (n-x)(n-y)$, which is an increasing function of both $x$ and $y$. In particular, this difference is maximal

when $x$ and $y$ equal $n - 1$ and $n - 2$. Fortunately, this yields precisely the difference between the claimed upper bound for $n$ and the assumed upper bound for $n - 1$, completing the induction.

B-4 Suppose such a matrix $A$ exists. If the eigenvalues of $A$ (over the complex numbers) are distinct, then there exists a complex matrix $C$ such that $B = CAC^{-1}$ is diagonal. Consequently, $\sin B$ is diagonal. But then $\sin A = C^{-1}(\sin B)C$ must be diagonalizable, a contradiction. Hence the eigenvalues of $A$ are the same, and $A$ has a conjugate $B= CAC^{-1}$ over the complex numbers of the form

A direct computation shows that

Since $\sin A$ and $\sin B$ are conjugate, their eigenvalues must be the same, and so we must have $\sin x = 1$. This implies $\cos x = 0$, so that $\sin B$ is the identity matrix, as must be $\sin A$, a contradiction. Thus $A$ cannot exist.

Alternate solution (due to Craig Helfgott and Alex Popa): Define both $\sin A$ and $\cos A$ by the usual power series. Since  $A$ commutes with itself, the power series identity

holds. But if $\sin A$ is the given matrix, then by the above
identity, $\cos^{2}A$ must equal $\left(\begin{array}{cc} 0 & -2 \cdot 1996 \\ 0 & 0 \end{array}\right)$ which is a
nilpotent matrix. Thus $\cos A$ is also nilpotent. However, the square of any $2 \times 2$ nilpotent matrix must be
zero (e.g., by the Cayley-Hamilton theorem). This is a
contradiction.

B-5 Consider a $1 \times n$ checkerboard, in which we write an
$n$-letter string, one letter per square. If the string is
balanced, we can cover each pair of adjacent squares
containing the same letter with a $1 \times 2$ domino, and
these will not overlap (because no three in a row can
be the same). Moreover, any domino is separated from
the next by an even number of squares, since they must
cover opposite letters, and the sequence must alternate
in between.

Conversely, any arrangement of dominoes where adjacent dominoes are separated by an even number of squares corresponds to a unique balanced string, once we choose whether the string starts with $X$ or $O$. In other words, the number of balanced strings is twice the number of acceptable domino arrangements.

We count these arrangements by numbering the squares $0, 1, \ldots, n - 1$ and distinguishing whether the dominoes start on even or odd numbers. Once this is decided, one
