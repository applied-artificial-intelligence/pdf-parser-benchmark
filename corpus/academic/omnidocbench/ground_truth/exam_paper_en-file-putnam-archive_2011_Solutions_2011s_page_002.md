A5 (by Abhinav Kumar) Define $G : \mathbb{R} \to \mathbb{R}$ by $G(x) = \int_0^x g(t)dt$. By assumption, $G$ is a strictly increasing,
thrice continuously differentiable function. It is also
bounded: for $x > 1$, we have

and similarly, for $x < -1$, we have $0 > G(x) - G(-1) \geq$
-1. It follows that the image of $G$ is some open interval
$(A, B)$ and that $G^{-1} : (A, B) \to \mathbb{R}$ is also thrice continuously differentiable.

Define $H : (A,B) \times (A,B) \to \mathbb{R}$ by $H(x,y) =$
$F(G^{-1}(x),G^{-1}(y))$; it is twice continuously differentiable since $F$ and $G^{-1}$ are. By our assumptions
about $F$,

Therefore \(H\) is constant along any line parallel to the vector \((1,1)\), or equivalently, \(H(x,y)\) depends only on \(x-y\). We may thus write \(H(x,y) = h(x-y)\) for some function \(h\) on \((-(B-A), B-A)\), and we then have \(F(x,y) = h(G(x) - G(y))\). Since \(F(u,u) = 0\), we have \(h(0) = 0\). Also, \(h\) is twice continuously differentiable (since it can be written as \(h(x) = H((A+B+x)/2, (A+B-x)/2)\)). So \(|h'|\) is bounded on the closed interval \([-(B-A)/2, (B-A)/2]\), say by \(M\).

Given $x_1, \ldots, x_{n+1} \in \mathbb{R}$ for some $n \geq 2$, the numbers $G(x_1), \ldots, G(x_{n+1})$ all belong to $(A,B)$, so we can choose indices $i$ and $j$ so that $|G(x_i) - G(x_j)| \leq (B-A)/n \leq (B-A)/2$. By the mean value theorem,

so the claim holds with $C = M ( B - A )$

A6 Choose some ordering $h_1, \ldots, h_n$ of the elements of $G$ with $h_1 = e$. Define an $n \times n$ matrix $M$ by setting $M_{ij} = 1/k$ if $h_j = h_i g$ for some $g \in \{g_1, \ldots, g_k\}$ and $M_{ij} = 0$ otherwise. Let $v$ denote the column vector $(1, 0, \ldots, 0)$. The probability that the product of $m$ random elements of $\{g_1, \ldots, g_k\}$ equals $h_i$ can then be interpreted as the $i$-th component of the vector $M^m v$.

Let $\hat{G}$ denote the dual group of $G$, i.e., the group
of complex-valued characters of $G$. Let $\hat{e} \in \hat{G}$ denote the trivial character. For each $\chi \in \hat{G}$, the vector
$v_{\chi}=(\chi(h_i))_{i=1}^n$ is an eigenvector of $M$ with eigenvalue
$\lambda_{\chi}=(\chi(g_1)+\cdots+\chi(g_k))/k$. In particular, $v_{\hat{e}}$ is the
all-ones vector and $\lambda_{\hat{e}}=1$. Put

we show that $b \in (0, 1)$ as follows. First suppose $b = 0$;
then

because $\sum_{\chi \in \hat{G}} \chi(g_i)$ equals $n$ for $i=1$ and 0 otherwise. However, this contradicts the hypothesis that $\{g_1, \ldots, g_k\}$ is not all of $G$. Hence $b>0$. Next suppose $b=1$, and choose $\chi \in \hat{G} - \{\hat{e}\}$ with $|\lambda_\chi|=1$. Since each of $\chi(g_1), \ldots, \chi(g_k)$ is a complex number of norm 1, the triangle inequality forces them all to be equal. Since $\chi(g_1) = \chi(e) = 1$, $\chi$ must map each of $g_1, \ldots, g_k$ to 1, but this is impossible because $\chi$ is a nontrivial character and $g_1, \ldots, g_k$ form a set of generators of $G$. This contradiction yields $b<1$.

Since $\nu = \frac{1}{n}\sum_{\chi \in \hat{G}} \nu_{\chi}$ and $M \nu_{\chi} = \lambda_{\chi} \nu_{\chi}$, we have

Since the vectors $v_{\chi}$ are pairwise orthogonal, the limit
we are interested in can be written as

and then rewritten as

By construction,this last quantity is nonzero and finite.

Remark. It is easy to see that the result fails if we do not assume $g_1 = e$: take $G = \mathbb{Z}/2\mathbb{Z}$, $n = 1$, and $g_1 = 1$.

Remark. Harm Derksen points out that a similar argument applies even if G is not assumed to be abelian, provided that the operator $g_1 + \cdots + g_k$ in the group algebra $\mathbb{Z}[G]$ is normal, i.e., it commutes with the operator $g_1^{-1} + \cdots + g_k^{-1}$. This includes the cases where the set $\{g_1, \ldots, g_k\}$ is closed under taking inverses and where it is a union of conjugacy classes (which in turn includes the case of G abelian).

Remark. The matrix $M$ used above has nonnegative
entries with row sums equal to 1 (i.e., it corresponds to
a Markov chain), and there exists a positive integer $m$
such that $M^m$ has positive entries. For any such matrix,
the Perron-Frobenius theorem implies that the sequence
of vectors $M^m \nu$ converges to a limit $w$, and there exists
$b \in [0, 1)$ such that

is nonzero and finite. (The intended interpretation in case $b=0$ is that $M^m v = w$ for all large $m$.) However, the limit need not exist in general.
