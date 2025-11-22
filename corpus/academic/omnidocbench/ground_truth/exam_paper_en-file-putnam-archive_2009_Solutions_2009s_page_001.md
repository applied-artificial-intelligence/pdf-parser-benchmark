# Solutions to the 7Oth WilliamLowell Putnam Mathematical Competition

# Saturday, December 5, 2009

Kiran Kedlaya and Lenny $\mathrm { N g }$

A-1 Yes,it does follow.Let $P $be any point in the plane.Let $A B C D$ be any square with center $P$ .Let $E , F , G , H $be the midpoints of the segments $A B , B C , C D , D A$ ,respectively. The function $f $must satisfy the equations

If we add the last four equations,then subtract the first equation and twice the second equation,we obtain $0 = 4 f (P) $,whence $f (P) = 0 $

Remark.Problem 1 of the 1996 Romanian IMO team selection exam asks the same question with squares replaced by regular polygons of any(fixed) number of vertices.

A-2 Multiplying the first differential equation by $g h$ ,the second by$ f h$ ,and the third by $f g$ ,and summing gives

Write $k(x) = f(x)g(x)h(x)$; then $k' = 6k^2 + 6$ and $k(0) =$
1. One solution for this differential equation with this
initial condition is $k(x) = \tan(6x + \pi/4)$; by standard
uniqueness, this must necessarily hold for $x$ in some
open interval around 0. Now the first given equation
becomes

integrating both sides gives

whence $f(x) = e^c \left( \frac{\sin(6x+\pi/4)}{\cos^2(6x+\pi/4)} \right)^{1/6}$. Substituting $f(0) = 1$ gives $e^c = 2^{-1/12}$ and thus $f(x) = 2^{-1/12} \left( \frac{\sin(6x+\pi/4)}{\cos^2(6x+\pi/4)} \right)^{1/6}$.

Remark.The answer can be put in alternate forms using trigonometric identities. One particularly simple one is

A-3 The limit is 0; we will show this by checking that
$d_n=0$ for all $n \ge 3$. Starting from the given matrix,
add the third column to the first column; this does not
change the determinant. However, thanks to the identity
$\cos x + \cos y = 2 \cos \frac{x+y}{2} \cos \frac{x-y}{2}$, the resulting matrix has
the form

with the first column being a multiple of the second.
Hence $d_{n}=0$.

Remark. Another way to draw the same conclusion is to observe that the given matrix is the sum of
the two rank 1 matrices $A_{jk} = \cos(j-1)n\cos k$ and
$B_{jk} = -\sin(j-1)n\sin k$, and so has rank at most 2.
One can also use the matrices $A_{jk} = e^{i((j-1)n+k)}, B_{jk} =$
$e^{-i((j-1)n+k)}$.

A-4 The answer is no; indeed, $S = \mathbb{Q}\setminus\{n+2/5 | n \in \mathbb{Z}\}$ sat-isfies the given conditions. Clearly S satisfies (a) and (b); we need only check that it satisfies (c). It suffices to show that if $x = p/q$ is a fraction with $(p,q) = 1$ and $p > 0$, then we cannot have $1/(x(x-1)) = n+2/5$ for an integer n. Suppose otherwise; then

Since $p$ and $q$ are relatively prime, and $p$ divides
$5q^2$, we must have $p|5$, so $p=1$ or $p=5$. On the
other hand, $p-q$ and $q$ are also relatively prime, so
$p-q$ divides 5 as well, and $p-q$ must be $\pm 1$ or
$\pm 5$. This leads to eight possibilities for $(p,q)$: $(1,0)$,
$(5,0)$, $(5,10)$, $(1,−4)$, $(1,2)$, $(1,6)$, $(5,4)$, $(5,6)$. The
first three are impossible, while the final five lead to
$5n+2 = 16,−20,−36,16,−36$ respectively, none of
which holds for integral $n$.

Remark. More generally, no rational number of the form $m/n$, where $m,n$ are relatively prime and neither of $\pm m$ is a quadratic residue mod $n$, need be in $S$. If $x=p/q$ is in lowest terms and $1/(x(x-1)) = m/n+k$ for some integer $k$, then $p(p-q)$ is relatively prime to $q^2$; $q^2/(p(p-q)) = (m+kn)/n$ then implies that $m+kn = \pm q^2$ and so $\pm m$ must be a quadratic residue mod $n$.

A-5 No,there is no such group.By the structure theorem for finitely generated abelian groups, $G$ can be written as a product of cyclic groups.If any of these factors has odd order, then $G$ has an element of odd order,so the
