by comparing the sum to an integral. This gives

We now interpret $f(n)$ as counting the number of $n$-tuples $(a_1, \ldots, a_n)$ of nonnegative integers such that

For an upper bound on $f(n)$, we use the inequalities $0 \le a_i \le n!/i!$ to deduce that there are at most $n!/i! + 1 \le 2(n!/i!)$ choices for $a_i$. Hence

For a lower bound on $f(n)$, we note that if $0 \leq a_i < (n-1)!/i!$ for $i = 2, \ldots, n-1$ and $a_n = 0$, then $0 \leq a_2 2! + \cdots + a_n n! \leq n!$, so there is a unique choice of $a_1$ to complete this to a solution of $a_1 1! + \cdots + a_n n! = n!$.
Hence
