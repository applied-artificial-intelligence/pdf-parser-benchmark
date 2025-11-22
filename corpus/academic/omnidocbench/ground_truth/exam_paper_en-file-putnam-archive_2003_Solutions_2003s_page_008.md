where

Consider the partial sum $P_k = \sum_{j=1}^k C_j$. If exactly $p_k$ of $a_1, \ldots, a_k$ are positive, then this sum is equal to

which expands and simplifies to

For $k \le 2p$ even, this partial sum would be minimized
with $p_k = \frac{k}{2}$, and would then equal $-\frac{k}{2}$; for $k < 2p$ odd,
this partial sum would be minimized with $p_k = \frac{k \pm 1}{2}$, and
would then equal $-\frac{k-1}{2}$. Either way, $P_k \ge -\lfloor \frac{k}{2} \rfloor$. On the
other hand, if $k > 2p$, then

since $p_k$ is at most $p$. Define $Q_k$ to be $-\lfloor \frac{k}{2} \rfloor$ if $k \leq 2p$ and $-2p(k-p) + \binom{k}{2}$ if $k \geq 2p$, so that $P_k \geq Q_k$. Note that $Q_1 = 0$.

Partial summation gives

It follows that

as desired. The next-to-last and last inequalities each
follow from the monotonicity of the $r_i$'s, the former by
pairing the $i^{\mathrm{th}}$ term with the $(2p + 1 - i)^{\mathrm{th}}$.

Note: Compare the closely related Problem 6 from the 2000 USA Mathematical Olympiad: prove that for any nonnegative real numbers $a_1, \dots, a_n, b_1, \dots, b_n$, one has
