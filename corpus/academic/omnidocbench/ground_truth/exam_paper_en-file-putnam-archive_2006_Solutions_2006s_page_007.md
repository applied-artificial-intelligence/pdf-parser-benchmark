as desired.

Remark: The use of Cesaro's lemma above is the special case $b_n = n$ of the Cesaro-Stolz theorem: if $a_n, b_n$
are sequences such that $b_n$ is positive, strictly increasing, and unbounded, and

then

Second solution: In this solution, rather than applying Taylor's theorem with remainder to $(1+x)^m$ for $1 < m < 2$ and $x > 0$, we only apply convexity to deduce that $(1+x)^m \ge 1+mx$. This gives

and so

for some $c \in \mathbb{R}$. In particular,

and so

But turning this around, the fact that

where $o(1)$ denotes a function tending to 0 as $n \to \infty$,
yields

so

and this completes the proof.

Third solution: We argue that $a_{n} \to \infty$ as in the first
solution. Write $b_{n} = a_{n} - L n^{k/(k+1)}$, for a value of $L$ to
be determined later. We have

where

We first estimate $e_1$. For $-1 < m < 0$, by the convexity of $(1+x)^m$ and $(1+x)^{1-m}$, we have

Hence

Note that both bounds have sign opposite to $b_n$; moreover, by the bound $a_n = \Omega(n^{(k-1)/k})$, both bounds have
absolutely value strictly less than that of $b_n$ for $n$ sufficiently large. Consequently, for $n$ large,

We now work on $e_{2}$. By Taylor’s theorem with remainder applied to $(1 + x)^{m}$ for $x > 0$ and $0 < m < 1$,

The “main term” of $L((n+1)^{k/(k+1)} - n^{k/(k+1)})$
is $L\frac{k}{k+1}n^{-1/(k+1)}$. To make this coincide with
$L^{-1/k}n^{-1/(k+1)}$, we take

We then find that

and because $b_{n+1} = e_{1} + e_{2}$, we have $|b_{n+1}| \leq |b_{n}| + |e_{2}|$. Hence
