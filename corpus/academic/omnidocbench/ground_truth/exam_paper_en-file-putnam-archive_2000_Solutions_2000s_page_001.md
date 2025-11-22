# Solutions to the 61st William Lowell Putnam Mathematical Competition

# Solutions to the 6lst William Lowell Putnam Mathematical Competition Saturday, December 2,2000

Manjul Bhargava,Kiran Kedlaya,and Lenny Ng

A-1 The possible values comprise the interval $(0, A^2)$.

To see that the values must lie in this interval, note that

so $\sum_{j=0}^{m} x_j^2 \leq A^2 - 2x_0x_1$. Letting $m \to \infty$, we have
$\sum_{j=0}^{\infty} x_j^2 \leq A^2 - 2x_0x_1 < A^2.$

To show that all values in $(0,A^2)$ can be obtained, we use geometric progressions with $x_1/x_0 = x_2/x_1 = \cdots = d$ for variable $d$. Then $\sum_{j=0}^\infty x_j = x_0/(1-d)$ and

As $d$ increases from 0 to 1, $(1-d)/(1+d)$ decreases from 1 to 0. Thus if we take geometric progressions with $\sum_{j=0}^{\infty}x_j=A$, $\sum_{j=0}^{\infty}x_j^2$ ranges from 0 to $A^2$. Thus the possible values are indeed those in the interval $(0,A^2)$, as claimed.

A-2 First solution: Let $a$ be an even integer such that $a^2+1$
    is not prime. (For example, choose $a \equiv 2 \pmod 5$, so
    that $a^2+1$ is divisible by 5.) Then we can write $a^2+1$ as
    a difference of squares $x^2-b^2$, by factoring $a^2+1$ as $rs$
    with $r \ge s > 1$, and setting $x=(r+s)/2, b=(r-s)/2$.
Finally, put $n=x^2-1$, so that $n=a^2+b^2, n+1=x^2,
    n+2=x^2+1$.

Second solution: It is well-known that the equation
$x^2 - 2y^2 = 1$ has infinitely many solutions (the so-
called "Pell" equation). Thus setting $n = 2y^2$ (so that
$n = y^2 + y^2$, $n + 1 = x^2 + 0^2$, $n + 2 = x^2 + 1^2$) yields
infinitely many n with the desired property.

Third solution: As in the first solution, it suffices to exhibit x such that $x^2 - 1$ is the sum of two squares. We
will take $x = 3^{2^n}$, and show that $x^2 - 1$ is the sum of two
squares by induction on n: if $3^{2^n} - 1 = a^2 + b^2$, then

Fourth solution (by Jonathan Weinstein): Let $n = 4k^{4} +$
$4k^{2} = (2k^{2})^{2} + (2k)^{2}$ for any integer $k$. Then $n + 1 =$
$(2k^{2} + 1)^{2} + 0^{2}$ and $n + 2 = (2k^{2} + 1)^{2} + 1^{2}.$

A-3 The maximum area is $3\sqrt{5}$.

We deduce from the area of $P_1P_3P_5P_7$ that the radius
of the circle is $\sqrt{5/2}$. An easy calculation using the

Pythagorean Theorem then shows that the rectangle $P_2P_4P_6P_8$ has sides $\sqrt{2}$ and $2\sqrt{2}$. For notational ease, denote the area of a polygon by putting brackets around the name of the polygon.

By symmetry,the area of the octagon can be expressed as

Note that $[P_2P_3P_4]$ is $\sqrt{2}$ times the distance from $P_3$ to
$P_2P_4$, which is maximized when $P_3$ lies on the midpoint
of arc $P_2P_4$; similarly, $[P_4P_5P_6]$ is $\sqrt{2}/2$ times the distance from $P_5$ to $P_4P_6$, which is maximized when $P_5$
lies on the midpoint of arc $P_4P_6$. Thus the area of
the octagon is maximized when $P_3$ is the midpoint of
arc $P_2P_4$ and $P_5$ is the midpoint of arc $P_4P_6$. In this
case, it is easy to calculate that $[P_2P_3P_4] = \sqrt{5}-1$ and
$[P_4P_5P_6] = \sqrt{5}/2-1$, and so the area of the octagon is
$3\sqrt{5}$.

A-4 To avoid some improper integrals at 0, we may as well replace the left endpoint of integration by some $ \varepsilon > 0$. We now use integration by parts:

Now $\frac{\sin x}{2x} \cos x^2$ tends to 0 as $B \to \infty$, and the integral
of $\frac{\sin x}{2x^2} \cos x^2$ converges absolutely by comparison with
$1/x^2$. Thus it suffices to note that

and that the final integral converges absolutely by comparison to $1/x^3$.

An alternate approach is to first rewrite $\sin x \sin x^2$ as
$\frac{1}{2}(\cos(x^2 - x) - \cos(x^2 + x))$. Then
