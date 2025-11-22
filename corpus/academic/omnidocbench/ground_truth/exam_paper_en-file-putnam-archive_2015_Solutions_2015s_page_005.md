- $(a)_n$ implies $(b)_n$;
- $ (a)_n $ and $ (b)_1, \ldots, (b)_n $ together imply $ (a)_{n+1} $.

To produce a value of n for which $s_n \equiv 2015\pmod {10000}$, we take $n = 3m+1$ for some nonnegative integer m for which $s_{3m+1} = 30m+15$. We must
also have $30m \equiv 2000\pmod {10000}$, or equivalently
$m \equiv 400\pmod {1000}$. By taking $m = 1400$, we ensure
that $m \equiv 2\pmod {3}$, so $s_m = 10m+7$; this ensures that
$s_n$ does indeed equal $30m+15 = 42015$, as desired.

Remark: With a bit more work, we can give a complete
description of $s_n$, and in particular find the first term in
the sequence whose decimal expansion ends in 2015.
Define the function on nonnegative integers

which takes values in $\{ - 1 , 0 , 1 \}$; we then have

Consequently, if we write $n$ in base 3, then $f(n) = 0$ unless the expansion ends with 2 followed by a string of 1s of length $k \geq 0$, in which case $f(n) = (-1)^{k+1}$.

In this notation, we have $s_n \equiv 2015 \pmod {10000}$ if and
only if $n = 3m+1$ for some nonnegative integer $m$ for
which $m \equiv 400\pmod {10000}$ and $f(m) = -1$. Since
$400 = 112211_{(3)}$, the first such term in the sequence is
in fact $s_{1201} = 12015$.

B3 First solution: Any element of $S$ can be written as $M = \alpha A + \beta B$, where $A =\binom {1~~1}{1~~1} $, $B = \binom {-3~-1}{~1~~~3}$, and $\alpha,\beta\in\mathbb{R}$. Note that $A^2 = \binom {4~~4}{4~~4}$ and $B^3=\binom {-24~-8}{~8~~~24}$ are both in $S$, and so any matrix of the form $\alpha A$ or $\beta B, \alpha, \beta \in \mathbb{R}$, satisfies the given condition.

We claim that these are also the only matrices in $S$ satisfying the given condition. Indeed, suppose $M = \alpha A + \beta B$ where $\alpha, \beta \neq 0$. Let $C=\binom {1~~1/\sqrt{2}}{-1~~1/\sqrt{2}}$ with inverse $C^{-1} =\binom {1/2~~-1/2~}{1/\sqrt{2}~~~1/\sqrt{2}}$. If we define $D=C^{-1}MC$, then $D =2\alpha \binom {0~~\gamma}{\gamma~~~1}$ where $\gamma = -\frac{\beta\sqrt{2}}{\alpha}$. Now suppose that $M^k$ is in $S$ with $k \geq 2$. Since $(1\; -1)A\binom {1}{-1} = (1\; -1)B\binom {1}{-1}=0$, we have $(1\; -1)M^k\binom {1}{-1} = 0$, and so the upper left entry of $C^{-1}M^kC = D^k$ is 0. On the other hand, from the expression for $D$, an easy induction on $k$ shows that $D^k = (2\alpha)^k \binom{\gamma^2 p_{k-1}~~ \gamma p_k }{\gamma p_k~~~p_{k+1}}$, where $p_k$ is defined inductively by $p_0=0, p_1=1, p_{k+2} = \gamma^2 p_k + p_{k+1}$. In particular, it follows from the inductive definition that $p_k > 0$ when $k \geq 1$, whence the upper left entry of $D^k$ is nonzero when $k \geq 2$, a contradiction.

Remark: A variant of this solution can be obtained by diagonalizing the matrix $M$.

Second solution: If $a , b , c , d$ are in arithmetic progression, then we may write

for some $r$, $s$. If $s$ = 0, then clearly all powers of $M$ are in $xS$. Also, if $r$ = 0, then one easily checks that $M^3$ is in $S$.

We now assume $rs \neq 0$, and show that in that case $M$
cannot be in $S$. First, note that the characteristic polynomial of $M$ is $x^2 - 2rx - 8s^2$, and since $M$ is nonsingular
(as $s \neq 0$), this is also the minimal polynomial of $M$ by
the Cayley-Hamilton theorem. By repeatedly using the
relation $M^2 = 2rM + 8s^2I$, we see that for each positive
integer, we have $M^k = t_k M + u_k I$ for unique real constants $t_k, u_k$ (uniqueness follows from the independence
of $M$ and $I$). Since $M$ is in $S$, we see that $M^k$ lies in $S$
only if $u_k = 0$.

On the other hand, we claim that if $k > 1$, then $rt_k > 0$ and $u_k > 0$ if $k$ is even, and $t_k > 0$ and $ru_k > 0$ if $k$ is odd (in particular, $u_k$ can never be zero). The claim is true for $k=2$ by the relation $M^2 = 2rM+8s^2I$. Assuming the claim for $k$, and multiplying both sides of the relation $M^k = t_kM + u_kI$ by $M$, yields

implying the claim for $k+1$.

Remark: (from artofproblemsolving.com, user hoei j) Once one has $u_k=0$, one can also finish using the relation $M \cdot M^k = M^k \cdot M$.

B4 First solution:The answer is $17/21$. For fixed $ b,c$, there is a triangle of side lengths $a , b , c$ if and only if $| b - c | < a < b + c$. It follows that the desired sum is

We write this as $S = S_{1} + S_{2}$ where $S_{1}$ sums over positive integers $b, c$ with $b \leq c$ and $S_{2}$ sums over $b > c$. Then
