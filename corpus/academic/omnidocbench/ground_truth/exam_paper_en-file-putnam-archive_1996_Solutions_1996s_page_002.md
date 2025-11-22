Therefore

so $(a_{j}, z, a_{j+1}) \notin S$. The case $j = i + 1$ is ruled out by

and the case $ j = i - 1$ is similar.

Finally, we put $g(z)$ in $(g(a_n), +\infty)$ if $i=n$, and $(g(a_i),g(a_{i+1}))$ otherwise; an analysis similar to that above shows that $g$ has the desired property.

A-5 (due to Lenny Ng) For $1 \leq n \leq p-1$, p divides $\binom{p}{n}$ and

where the congruence $x \equiv y (\bmod p)$ means that $x-y$ is a rational number whose numerator, in reduced form, is divisible by $p$. Hence it suffices to show that

We distinguish two cases based on $p \pmod{6}$.First suppose $p = 6 r + 1 $ ,so that $k = 4 r$ .Then

since $p = 6 r + 1$.

Now suppose $p = 6 r + 5$ ，so that $k = 4 r + 3$ . A similar argument gives

A-6  We first consider the case $c \leq 1/4$; we shall show in this
case $f$ must be constant. The relation

proves that $f$ is an even function. Let $r_1 \leq r_2$ be the
roots of $x^2 + c - x$, both of which are real. If $x > r_2$,

define $x_{0} = x$ and $x_{n+1} = \sqrt{x_{n} - c}$ for each positive integer $x$. By induction on $n$, $r_{2} < x_{n+1} < x_{n}$ for all $n$, so the sequence $\{x_{n}\}$ tends to a limit $L$ which is a root of $x^{2} + c = x$ not less than $r_{2}$. Of course this means $L = r_{2}$. Since $f(x) = f(x_{n})$ for all $n$ and $x_{n} \to r_{2}$, we conclude $f(x) = f(r_{2})$, so $f$ is constant on $x \geq r_{2}$.

If $r_1 < x < r_2$ and $x_n$ is defined as before, then by induction, $x_n < x_{n+1} < r_2$. Note that the sequence can be
defined because $r_1 > c$; the latter follows by noting that
the polynomial $x^2 - x + c$ is positive at $x=c$ and has
its minimum at $1/2 > c$, so both roots are greater than
$c$. In any case, we deduce that $f(x)$ is also constant on $r_1 \le x \le r_2$.

Finally, suppose $x < r_1$. Now define $x_0 = x, x_{n+1} = x_n^2+c$. Given that $x_n < r_1$, we have $x_{n+1} > x_n$. Thus if we had $x_n < r_1$ for all $n$, by the same argument as in the first case we deduce $x_n \to r_1$ and so $f(x) = f(r_1)$. Actually, this doesn't happen; eventually we have $x_n > r_1$, in which case $f(x) = f(x_n) = f(r_1)$ by what we have already shown. We conclude that $f$ is a constant function. (Thanks to Marshall Buck for catching an inaccuracy in a previous version of this solution.)

Now suppose $c > 1/4$. Then the sequence $x_n$ defined
by $x_0 = 0$ and $x_{n+1} = x_n^2 + c$ is strictly increasing and
has no limit point. Thus if we define $f$ on $[x_0, x_1]$ as any
continuous function with equal values on the endpoints,
and extend the definition from $[x_n, x_{n+1}]$ to $[x_{n+1}, x_{n+2}]$
by the relation $f(x) = f(x^2 + c)$, and extend the definition further to $x < 0$ by the relation $f(x) = f(-x)$, the
resulting function has the desired property. Moreover,
any function with that property clearly has this form.

B-1 Let $[n]$ denote the set $\{1,2,\dots,n\}$, and let $f_n$ denote
the number of minimal selfish subsets of $[n]$. Then the
number of minimal selfish subsets of $[n]$ not containing
$n$ is equal to $f_{n-1}$. On the other hand, for any minimal selfish subset of $[n]$ containing $n$, by subtracting 1
from each element, and then taking away the element
$n - 1$ from the set, we obtain a minimal selfish subset
of $[n-2]$ (since 1 and $n$ cannot both occur in a selfish
set). Conversely, any minimal selfish subset of $[n-2]$
gives rise to a minimal selfish subset of $[n]$ containing
$n$ by the inverse procedure. Hence the number of minimal selfish subsets of $[n]$ containing $n$ is $f_{n-2}$. Thus we
obtain $f_n = f_{n-1} + f_{n-2}$. Since $f_1 = f_2 = 1$, we have
$f_n = F_n$, where $F_n$ denotes the nth term of the Fibonacci
sequence.

B-2 By estimating the area under the graph of $\ln x$ using upper and lower rectangles of width 2, we get

Since $\int \ln x \, dx = x \ln x - x + C$, we have, upon exponen-
