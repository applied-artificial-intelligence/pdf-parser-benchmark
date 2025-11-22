for $i = 1, \ldots, n$ will have the properties that $N \equiv 1$ (mod $b$) and $b^2 < N < 2b^2$ for $m$ sufficiently large.

Note (due to Russ Mann): one can also give a “nonconstructive” argument. Let $N$ be a large positive integer.
For $b \in (N^2, N^3)$, the number of 3-digit base-$b$ palindromes in the range $[b^2, N^6 - 1]$ is at least

since there is a palindrome in each interval $[kb, (k + 1)b - 1]$ for $k = b, \ldots, b^2 - 1$. Thus the average number of bases for which a number in $[1, N^6 - 1]$ is at least

for some constant $c > 0$. Take $N$ so that the right side
exceeds 2002; then at least one number in $[1, N^6 - 1]$ is
a base-$b$ palindrome for at least 2002 values of $b$.

B-6 We prove that the determinant is congruent modulo $p$ to

(3)

We first check that

(4)

Since both sides are homogeneous as polynomials in $x$ and $y$ ,it suffices to check (4) for $x = 1$ ,as a congruence between polynomials.Now note that the right side has $0 , 1 , \ldots , p - 1$ as roots modulo $p$ ,as does the left side. Moreover,both sides have the same leading coefficient. Since they both have degree only $p$ ,they must then coincide.

We thus have

which is precisely the desired determinant.

Note: a simpler conceptual proof is as follows. (Everything in this paragraph will be modulo $p$.) Note that for any integers $a,b,c$, the column vector $[ax + by + cz, (ax + by + cz)^p, (ax + by + cz)^{p^2}]$ is a linear combination of the columns of the given matrix. Thus $ax + by + cz$ divides the determinant. In particular, all of the factors of (3) divide the determinant; since both (3) and the determinant have degree $p^2 + p + 1$, they agree up to a scalar multiple. Moreover, they have the same coefficient of $z^{p^2}y^p x$ (since this term only appears in the expansion of (3) when you choose the first term in each factor). Thus the determinant is congruent to (3), as desired.

Either argument can be used to generalize to a corresponding $n \times n$ determinant, called a Moore determi-
nant; we leave the precise formulation to the reader.
Note the similarity with the classical Vandermonde determinant: if A is the $n \times n$ matrix with $A_{ij} = x_i^j$ for
$i, j=0, \ldots, n-1$, then
