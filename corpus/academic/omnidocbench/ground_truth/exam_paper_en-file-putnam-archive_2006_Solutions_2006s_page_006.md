Zaslavsky, Extremal arrangements of hyperplanes, Ann. N. Y. Acad. Sci. 440 (1985), 69-87.

B-4 The maximum is $2^k$, achieved for instance by the subspace

First solution: More generally, we show that any affine
k-dimensional plane in $\mathbb{R}^n$ can contain at most $2^k$ points in $Z$. The proof is by induction on $k+n$; the case $k=$
$n=0$ is clearly true.

Suppose that $V$ is a $k$-plane in $\mathbb{R}^n$. Denote the hyperplanes $\{x_n = 0\}$ and $\{x_n = 1\}$ by $V_0$ and $V_1$, respectively. If $V \cap V_0$ and $V \cap V_1$ are each at most $(k-1)$-dimensional, then $V \cap V_0 \cap Z$ and $V \cap V_1 \cap Z$ each have cardinality at most $2^{k-1}$ by the induction assumption, and hence $V \cap Z$ has at most $2^k$ elements. Otherwise, if $V \cap V_0$ or $V \cap V_1$ is $k$-dimensional, then $V \subset V_0$ or $V \subset V_1$; now apply the induction hypothesis on $V$, viewed as a subset of $\mathbb{R}^{n-1}$ by dropping the last coordinate.

Second solution: Let $S$ be a subset of $Z$ contained in a $k$-dimensional subspace of $V$. This is equivalent to asking that any $t_1, \ldots, t_{k+1} \in S$ satisfy a nontrivial linear dependence $c_1 t_1 + \cdots + c_{k+1} t_{k+1} = 0$ with $c_1, \ldots, c_{k+1} \in \mathbb{R}$. Since $t_1, \ldots, t_{k+1} \in \mathbb{Q}^n$, given such a dependence we can always find another one with $c_1, \ldots, c_{k+1} \in \mathbb{Q}$; then by clearing denominators, we can find one with $c_1, \ldots, c_{k+1} \in \mathbb{Z}$ and not all having a common factor.

Let $\mathbb{F}_2$ denote the field of two elements, and let $\bar{S} \subseteq \mathbb{F}_2^n$ be the reductions modulo 2 of the points of $S$. Then any $t_1, \ldots, t_{k+1} \in \bar{S}$ satisfy a nontrivial linear dependence, because we can take the dependence from the end of the previous paragraph and reduce modulo 2. Hence $\bar{S}$ is contained in a $k$-dimensional subspace of $\mathbb{F}_{2n}$, and the latter has cardinality exactly $2^k$. Thus $\bar{S}$ has at most $2^k$ elements, as does $S$.

Variant (suggested by David Savitt): if $\bar S$ contained $k+1$ linearly independent elements, the $(k+1) \times n$ matrix formed by these would have a nonvanishing maximal minor. The lift of that minor back to $\mathbb{R}$ would also not vanish, so $S$ would contain $k+1$ linearly independent elements.

Third solution: (by Catalin Zara) Let $V$ be a $k$-dimensional subspace. Form the matrix whose rows are
the elements of $V \cap Z$; by construction, it has row rank
at most $k$. It thus also has column rank at most $k$; in
particular, we can choose $k$ coordinates such that each
point of $V \cap Z$ is determined by those $k$ of its coordinates. Since each coordinate of a point in $Z$ can only
take two values, $V \cap Z$ can have at most $2^k$ elements.

Remark: The proposers probably did not realize that this problem appeared online about three months before the exam, at http://www.artofproblemsolving.com/ Forum/viewtopic.php?t $= $ 105991. (It may very well have also appeared even earlier.)

B-5 The answer is $1/16$. We have

with equality when $f ( x ) = x / 2$.

B-6 First solution: We start with some easy upper and
lower bounds on $a_n$. We write $O(f(n))$ and $\Omega(f(n))$
for functions $g(n)$ such that $f(n)/g(n)$ and $g(n)/f(n)$,
respectively, are bounded above. Since $a_n$ is a non-decreasing sequence, $a_{n+1} - a_n$ is bounded above, so
$a_n = O(n)$. That means $a_n^{-1/k} = \Omega(n^{-1/k})$, so

In fact, all we will need is that $a_n \to \infty$ as $n \to \infty$.

By Taylor's theorem with remainder, for $1 < m < 2$ and $ x > 0$,

Taking $m = (k+1)/k$ and $x = a_{n+1}/a_n = 1 + a_n^{-(k+1)/k}$, we obtain

In particular,

In general, if $x_n$ is a sequence with $\lim_{n \to \infty} x_n = c$, then
also

by Cesaro’s lemma. Explicitly, for any $\varepsilon > 0$, we can find $N$ such that $\left|x_{n} - c\right| \leq \varepsilon/2$ for $n \geq N$, and then

for $n$ large, the right side is smaller than $\varepsilon$.

In our case, we deduce that

and so
