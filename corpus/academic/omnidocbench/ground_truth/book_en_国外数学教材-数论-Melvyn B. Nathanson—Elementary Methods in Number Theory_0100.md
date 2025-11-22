**Proof.** This follows immediately from Theorem 3.3, since $|(\mathbf{Z}/p\mathbf{Z})^{\times}| = p - 1$. □

The following table lists the primitive roots for the first six primes.

Let $p$ be a prime, and let $g$ be a primitive root modulo $p$. If $a$ is an integer not divisible by $p$，then there exists a unique integer $ k$ such that

and

This integer $k$ is called the index of $a$ with respect to the primitive root $g$, and is denoted by

If $k_1$ and $k_2$ are any integers such that $k_1 \leq k_2$ and

then

and so

If $a \equiv g^k \pmod{p}$ and $b \equiv g^\ell \pmod{p}$, then $ab \equiv g^k g^\ell = g^{k+\ell} \pmod{p}$,
and so

The index map $\mathrm{ind}_g$ is also called the discrete logarithm to the base $g$ modulo $p$.

For example, 2 is a primitive root modulo 13. Here is a table of $\operatorname{ind}_{2}(a)$ for $a=1, \ldots, 12$:

## 3. Primitive Roots and Quadratic Reciprocity
