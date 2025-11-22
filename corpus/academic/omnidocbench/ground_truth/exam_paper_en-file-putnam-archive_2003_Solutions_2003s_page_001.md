# Solutions to the 64th William Lowell Putnam Mathematical Competition

# Saturday, December 6, 2003

Manjul Bhargava, Kiran Kedlaya, and Lenny Ng

A1 There are $n$ such sums. More precisely, there is exactly one such sum with $k$ terms for each of $k = 1,\ldots,n$ (and clearly no others). To see this, note that if $n = a_1 + a_2 + \cdots + a_k$ with $a_1 \leq a_2 \leq \cdots \leq a_k \leq a_1 + 1$, then

However, there is a unique integer $a_1$ satisfying these
inequalities, namely $a_1 = \lfloor n/k \rfloor$. Moreover, once $a_1$ is
fixed, there are $k$ different possibilities for the sum $a_1 +$
$a_2 + \cdots + a_k$: if $i$ is the last integer such that $a_i = a_1$,
then the sum equals $ka_1 + (i - 1)$. The possible values
of $i$ are $1, \ldots, k$, and exactly one of these sums comes
out equal to $n$, proving our claim.

Note: In summary, there is a unique partition of $n$ with  $k$ terms that is "as equally spaced as possible" . One can also obtain essentially the same construction inductively: except for the all-ones sum, each partition of $n$ is obtained by "augmenting" a unique partition of $n - 1$.

A2  First solution: Assume without loss of generality that
$a_i + b_i > 0$ for each $i$ (otherwise both sides of the desired inequality are zero). Then the AM-GM inequality gives

and likewise with the roles of $a$ and $b$ reversed. Adding these two inequalities and clearing denominators yields the desired result.

Second solution: Write the desired inequality in the form

expand both sides, and compare the terms on both sides in which $k$ of the terms are among the $a_i$. On the left, one has the product of each $k$-element subset of $\{1,\dots,n\}$; on the right, one has

which is precisely $\binom{n}{k}$ times the geometric mean of
the terms on the left. Thus AM-GM shows that the
terms under consideration on the left exceed those on
the right; adding these inequalities over all $k$ yields the
desired result.

Third solution: Since both sides are continuous in each
$a_i$, it is sufficient to prove the claim with $a_1, \ldots, a_n$ all
positive (the general case follows by taking limits as
some of the $a_i$ tend to zero). Put $r_i = b_i/a_i$; then the
given inequality is equivalent to

In terms of the function

and the quantities $s_{i} = \log r_{i}$, we can rewrite the desired
inequality as

This will follow from Jensen's inequality if we can verify that $f$ is a convex function; it is enough to check that $f ^ { \prime \prime } ( x ) > 0$ for all $x$ . In fact,

is an increasing function of $x$, so $f''(x) > 0$ and Jensen's inequality thus yields the desired result. (As long as the $a_i$ are all positive, equality holds when $s_1 = \cdots = s_n$, i.e., when the vectors $(a_1,\ldots,a_n)$ and $(b_1,\ldots,b_n)$. Of course other equality cases crop up if some of the $a_i$ vanish, i.e., if $a_1 = b_1 = 0$.)

Fourth solution: We apply induction on $n$, the case $n = 1$ being evident. First we verify the auxiliary inequality

for $a,b,c,d \geq 0$. The left side can be written as

Applying the weighted AM-GM inequality between matching terms in the two sums yields
