# Solutions to the 60th William Lowell Putnam Mathematical Competition

# Saturday, December 4, 1999

Manjul Bhargava, Kiran Kedlaya, and Lenny Ng

A-1  Note that if $r ( x )$ and $s ( x )$ are any two functions, then

Therefore, if $F ( x )$ is the given function, we have

so we may set $f(x) = (3x+3)/2$, $g(x) = 5x/2$, and
$h(x) = -x + \frac{1}{2}$.

A-2 First solution: First factor $p ( x ) = q ( x ) r ( x )$ ,where $q$ has all real roots and $r$ has all complex roots. Notice that each root of $q$ has even multiplicity, otherwise $p$ would have a sign change at that root. Thus $q ( x )$ has a square root $s ( x )$ .

Now write $r(x) = \prod_{j=1}^{k}(x - a_j)(x - \overline{a_j})$ (possible because $r$ has roots in complex conjugate pairs). Write $\prod_{j=1}^{k}(x - a_j) = t(x) + iu(x)$ with $t,x$ having real coefficients. Then for $x$ real,

(Alternatively, one can factor $r ( x )$ as a product of quadratic polynomials with real coefficients, write each as a sum of squares, then multiply together to get a sum of many squares.)

Second solution: We proceed by induction on the degree of $p$, with base case where $p$ has degree 0. As in
the first solution, we may reduce to a smaller degree in
case $p$ has any real roots, so assume it has none. Then
$p(x) > 0$ for all real $x$, and since $p(x) \to \infty$ for $x \to \pm \infty$,
$p$ has a minimum value $c$. Now $p(x) - c$ has real roots,
so as above, we deduce that $p(x) - c$ is a sum of squares.
Now add one more square, namely $(\sqrt{c})^2$, to get $p(x)$
as a sum of squares.

A-3 First solution: Computing the coefficient of $x^{n+1}$ in the
identity $(1-2x-x^2)\textstyle\sum_{m=0}^{\infty}a_m x^m = 1$ yields the recurrence $a_{n+1} = 2a_n + a_{n-1}$; the sequence $\{a_n\}$ is then
characterized by this recurrence and the initial conditions $a_0=1, a_1=2$.

Define the sequence $\{b_n\}$ by $b_{2n} = a_{n-1}^2 + a_n^2, b_{2n+1} =$

$a_n(a_{n-1} + a_{n+1}).$ Then

and similarly $2b_{2n} + b_{2n-1} = b_{2n+1}$, so that $\left\{b_n\right\}$ satisfies the same recurrence as $\left\{a_n\right\}$. Since further $b_0 = 1, b_1 = 2$ (where we use the recurrence for $\left\{a_n\right\}$ to calculate $a_{-1} = 0$), we deduce that $b_n = a_n$ for all $n$. In particular, $a_n^2 + a_{n+1}^2 = b_{2n+2} = a_{2n+2}$.

Second solution: Note that

and that

so that

A  simple computation (omitted here) now shows that
$a_n^2+a_{n+1}^2=a_{2n+2}$.

Third solution (by Richard Stanley): Let $A$ be the matrix $ \begin{pmatrix} 0 & 1 \\ 1 & 2 \end{pmatrix} $. A simple induction argument shows that

The desired result now follows from comparing the top left corner entries of the equality $A^{n+2}A^{n+2}=A^{2n+4}$.

A-4 Denote the series by $S$, and let $a_{n}=3^{n}/n$. Note that

where the second equality follows by interchanging $m$
