B-5 First solution: Put $Q = x_1^2 + \cdots + x_n^2$. Since $Q$ is homogeneous, $P$ is divisible by $Q$ if and only if each of the homogeneous components of $P$ is divisible by $Q$. It is thus sufficient to solve the problem in case $P$ itself is homogeneous, say of degree $d$.

Suppose that we have a factorization $P = \mathcal{Q}^m R$ for some
$m > 0$, where $R$ is homogeneous of degree $d$ and not
divisible by $\mathcal{Q}$; note that the homogeneity implies that

Write $\nabla^2$ as shorthand for $\frac{\partial^2}{\partial x_1^2} + \cdots + \frac{\partial^2}{\partial x_n^2}$; then

Since $m > 0$, this forces $R$ to be divisible by $\mathcal{Q}$, contradiction.

Second solution: (by Noam Elkies) Retain notation as in the first solution. Let $P_d$ be the set of homogeneous polynomials of degree $d$, and let $H_d$ be the subset of $P_d$ of polynomials killed by $\nabla^2$, which has dimension $\geq \dim(P_d) - \dim(P_{d-2})$; the given problem amounts to showing that this inequality is actually an equality.

Consider the operator $Q\nabla^2$ (i.e., apply $\nabla^2$ then multiply
by $\mathcal{Q}$) on $P_d$; its zero eigenspace is precisely $H_d$. By the
calculation from the first solution, if $R \in P_d$, then

Consequently, $Q^j H_{d-2j}$ is contained in the eigenspace
of $Q\nabla^2$ on $P_d$ of eigenvalue

In particular, the $Q^j H^{d-2j}$ lie in distinct eigenspaces,
so are linearly independent within $P_d$. But by dimension counting, their total dimension is at least that of $P_d$.
Hence they exhaust $P_d$, and the zero eigenspace cannot
have dimension greater than $\dim(P_d) - \dim(P_{d-2})$, as
desired.

Third solution: (by Richard Stanley) Write x =
$(x_1, \dots, x_n)$ and $\nabla = (\frac{\partial}{\partial x_1}, \dots, \frac{\partial}{\partial x_n})$. Suppose that
$P(x) = Q(x)(x_1^2 + \cdots + x_n^2)$. Then

On the other hand, if $P(x) = \sum_{\alpha} c_{\alpha}x^{\alpha}$ (where $\alpha = (\alpha_1, \ldots, \alpha_n)$ and $x^{\alpha} = x_1^{\alpha_1} \cdots x_n^{\alpha_n}$), then the constant term of $P(\boldsymbol{\nabla})P(x)$ is seen to be $\sum_{\alpha} c_{\alpha}^2$. Hence $c_{\alpha} = 0$ for all $\alpha$.

Remarks: The first two solutions apply directly over any field of characteristic zero. (The result fails

in characteristic $p > 0$ because we may take $P$ = $(x_{1}^{2}+\cdots+x_{n}^{2})^{p} = x_{1}^{2p}+\cdots+x_{n}^{2p}$.) The third solution can be extended to complex coefficients by replacing $P(\nabla)$ by its complex conjugate, and again the result may be deduced for any field of characteristic zero. Stanley also suggests Section 5 of the arXiv e-print math.CO/0502363 for some algebraic background for this problem.

B-6 First solution: Let $I$ be the identity matrix, and let $J_x$ be
the matrix with $x$'s on the diagonal and 1's elsewhere.
Note that $J_x - (x-1)I$, being the all 1's matrix, has rank
1 and trace $n$, so has $n-1$ eigenvalues equal to 0 and
one equal to $n$. Hence $J_x$ has $n-1$ eigenvalues equal to
$x-1$ and one equal to $x+n-1$, implying

On the other hand,we may expand the determinant as a sum indexed by permutations,in which case we get

Integrating both sides from 0 to 1 (and substituting $y = 1 - x$ ) yields

as desired.

Second solution: We start by recalling a form of the principle of inclusion-exclusion: if $f$ is a function on the power set of $\{ 1 , \ldots , n \}$ ,then

In this case we take $f(S)$ to be the sum of $\sigma(\pi)$ over all
permutations $\pi$ whose fixed points are exactly $S$. Then
$\sum_{U \supseteq T} f(U) = 1$ if $|T| \geq n - 1$ and 0 otherwise (since a
permutation group on 2 or more symbols has as many
even and odd permutations), so

The desired sum can thus be written, by grouping over fixed point sets, as
