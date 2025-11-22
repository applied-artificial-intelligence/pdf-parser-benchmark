Similarly,

We conclude that $S = S_1 + S_2 = \frac{17}{21}$.

Second solution: Recall that the real numbers $a, b, c$
form the side lengths of a triangle if and only if

and that if we put $x=2(s-a), y=2(s-b), z=2(s-c)$,

To generate all integer triples $(a,b,c)$ which form the
side lengths of a triangle, we must also assume that
$x,y,z$ are either all even or all odd. We may therefore
write the original sum as

To unify the two sums, we substitute in the first case
$x = 2u + 1$, $y = 2v + 1$, $z = 2w + 1$ and in the second
case $x = 2u + 2$, $y = 2v + 2$, $z = 2w + 2$ to obtain

B5 The answer is 4.

Assume $n \ge 3$ for the moment. We write the permutations $\pi$ counted by $P_n$ as sequences $\pi(1),\pi(2),\ldots,\pi(n)$. Let $U_n$ be the number of permutations counted by $P_n$ that end with $n-1,n$; let $V_n$ be the number ending in $n,n-1$; let $W_n$ be the number starting with $n-1$ and ending in $n-2,n$; let $T_n$ be the number ending in $n-2,n$ but not starting with $n-1$; and let $S_n$

be the number which has $n-1,n$ consecutively in that
order, but not at the beginning or end. It is clear that
every permutation $\pi$ counted by $P_n$ either lies in exactly
one of the sets counted by $U_n, V_n, W_n, T_n, S_n$, or is the
reverse of such a permutation. Therefore

By examining how each of the elements in the sets
counted by $U_{n+1}, V_{n+1}, W_{n+1}, T_{n+1}, S_{n+1}$ can be obtained from a (unique) element in one of the sets
counted by $U_n, V_n, W_n, T_n, S_n$ by suitably inserting the element $n+1$, we obtain the recurrence relations

Also, it is clear that $W_n=1$ for all $n$.

So far we have assumed $n \geq 3$, but it is straightforward
to extrapolate the sequences $P_n, U_n, V_n, W_n, T_n, S_n$ back
to $n = 2$ to preserve the preceding identities. Hence for
all $n \geq 2$,

as desired.

Remark: There are many possible variants of the
above solution obtained by dividing the permutations
up according to different features. For example, Karl
Mahlburg suggests writing

where $P_n'$ counts those permutations counted by $P_n$ for
which 1 occurs before 2, and $Q_n'$ counts those permutations counted by $P_n'$ for which $\pi(1) = 1$. One then has
the recursion
