We cannot have $a = 1$, since $1 - 2^n \neq 2001$ for any $n$.
Thus the only possibility is $a = 13$. One easily checks
that $a = 13, n = 2$ is a solution; all that remains is to
check that no other $n$ works. In fact, if $n > 2$, then
$13^{n+1} \equiv 2001 \equiv 1 \pmod{8}$. But $13^{n+1} \equiv 13 \pmod{8}$
since $n$ is even, contradiction. Thus $a = 13, n = 2$ is the unique solution.

Note: once one has that $n$ is even, one can use that
$2002 = a^{n+1} + 1 - (a+1)^n$ is divisible by $a+1$ to rule out cases.

A-6 The answer is yes. Consider the arc of the parabola
$y = Ax^2$ inside the circle $x^2 + (y - 1)^2 = 1$, where we
initially assume that $A > 1/2$. This intersects the circle
in three points, $(0,0)$ and $(\pm\sqrt{2A-1}/A, (2A-1)/A)$.
We claim that for $A$ sufficiently large, the length $L$ of
the parabolic arc between $(0,0)$ and $(\sqrt{2A-1}/A, (2A-1)/A)$ is greater than 2, which implies the desired result
by symmetry. We express $L$ using the usual formula for arclength:

where we have artificially introduced $-x$ into the integrand in the last step. Now, for $x \geq 0$,

since $\int_{0}^{\infty} dx/(2(x+1))$ diverges, so does $\int_{0}^{\infty}(\sqrt{1+x^2}-x) dx$. Hence, for sufficiently large $A$, we have $\int_{0}^{2\sqrt{2A-1}}(\sqrt{1+x^2}-x) dx > 2$, and hence $L > 2$.

Note: a numerical computation shows that one must take $A > 34.7$ to obtain $L > 2$, and that the maximum value of $L$ is about 4.0027, achieved for $A \approx 94.1$.

B-1 Let $R$ (resp. $B$) denote the set of red (resp. black) squares in such a coloring, and for $s \in R \cup B$, let $f(s)n+g(s)+1$ denote the number written in square $s$, where $0 \leq f(s),g(s) \leq n-1$. Then it is clear that the value of $f(s)$ depends only on the row of $s$, while the value of $g(s)$ depends only on the column of $s$. Since every row contains exactly $n/2$ elements of $R$ and $n/2$ elements of $B$,

Similarly, because every column contains exactly $n / 2$ elements of $R$ and $n / 2$ elements of $B$,

It follows that

as desired.

Note: Richard Stanley points out a theorem of Ryser (see Ryser, Combinatorial Mathematics, Theorem 3.1) that can also be applied. Namely, if $A$ and $B$ are $0–1$ matrices with the same row and column sums, then there is a sequence of operations on $2 \times 2$ matrices of the form

or vice versa,which transforms $A$ into $B$. If we identify 0 and 1 with red and black, then the given coloring and the checkerboard coloring both satisfy the sum condition. Since the desired result is clearly true for the checkerboard coloring, and performing the matrix operations does not affect this, the desired result follows in general.

B-2 By adding and subtracting the two given equations, we obtain the equivalent pair of equations

Multiplying the former by $x$ and the latter by $y$, then adding and subtracting the two resulting equations, we obtain another pair of equations equivalent to the given ones,

It follows that $x = (3^{1/5} + 1)/2$ and $y = (3^{1/5} - 1)/2$ is the unique solution satisfying the given equations.

B-3 Since $(k - 1/2)^2 = k^2 - k + 1/4$ and $(k + 1/2)^2 = k^2 + k + 1/4$, we have that $\langle n \rangle = k$ if and only if $k^2 - k + 1 \le n \le k^2 + k$. Hence
