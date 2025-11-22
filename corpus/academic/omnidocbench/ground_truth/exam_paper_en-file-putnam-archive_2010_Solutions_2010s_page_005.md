B-5 First solution. The answer is no. Suppose otherwise. For the condition to make sense, $f$ must be differentiable. Since $f$ is strictly increasing, we must have $f'(x) \geq 0$ for all $x$. Also, the function $f'(x)$ is strictly increasing: if $y > x$ then $f'(y) = f(f(y)) > f(f(x)) = f'(x)$. In particular, $f'(y) > 0$ for all $y \in \mathbb{R}$.

For any $x_0 \geq -1$, if $f(x_0) = b$ and $f^{\prime}(x_0) = a > 0$, then $f^{\prime}(x) > a$ for $x > x_0$ and thus $f(x) \geq a(x-x_0) + b$ for $x \geq x_0$. Then either $b < x_0$ or $a = f^{\prime}(x_0) = f(f(x_0)) = f(b) \geq a(b-x_0) + b$. In the latter case, $b \leq a(x_0 + 1)/(a+1) \leq x_0 + 1$. We conclude in either case that $f(x_0) \leq x_0 + 1$ for all $x_0 \geq -1$.

It must then be the case that $f(f(x)) = f'(x) \leq 1$ for
all $x$, since otherwise $f(x) > x + 1$ for large $x$. Now by the above reasoning, if $f(0) = b_0$ and $f'(0) =$
$a_0 > 0$, then $f(x) > a_0x + b_0$ for $x > 0$. Thus for
$x > \max\{0, -b_0/a_0\}$, we have $f(x) > 0$ and $f(f(x)) >a_0x + b_0$. But then $f(f(x)) > 1$ for sufficiently large $x$, a contradiction.

Second solution. (Communicated by Catalin Zara.)
Suppose such a function exists. Since $f$ is strictly
increasing and differentiable, so is $f \circ f = f'$. In
particular, $f$ is twice differentiable; also, $f''(x) =$
$f'(f(x))f'(x)$ is the product of two strictly increasing
nonnegative functions, so it is also strictly increasing
and nonnegative. In particular, we can choose $\alpha > 0$ and $M \in \mathbb{R}$ such that $f''(x) > 4\alpha$ for all $x \geq M$. Then
for all $x \geq M,$

In particular, for some $M' > M$, we have $f(x) \geq \alpha x^{2}$ for
all $x \geq M'$.

Pick $T > 0$ so that $\alpha T^2 > M'$. Then for $x \geq T$, $f(x) > M'$ and so $f'(x) = f(f(x)) \geq \alpha f(x)^2$. Now

however, as $T \to \infty$, the left side of this inequality tends to 0 while the right side tends to $+\infty$, a contradiction.

Third solution. (Communicated by Noam Elkies.)
Since $f$ is strictly increasing, for some $y_{0}$, we can define the inverse function $g(y)$ of $f$ for $y \geq y_{0}$. Then

$x = g(f(x))$, and we may differentiate to find that $1 = g'(f(x))f'(x) = g'(f(x))f(f(x))$. It follows that $g'(y) = 1/f(y)$ for $y \geq y_0$; since $g$ takes arbitrarily large values, the integral $\int_{y_0}^{\infty} dy/f(y)$ must diverge. One then gets a contradiction from any reasonable lower bound on $f(y)$ for $y$ large, e.g., the bound $f(x) \geq \alpha x^2$ from the second solution. (One can also start with a linear lower bound $f(x) \geq \beta x$, then use the integral expression for $g$ to deduce that $g(x) \leq \gamma \log x$, which in turn forces $f(x)$ to grow exponentially.)

B-6 For any polynomial $p(x)$, let $[p(x)]A$ denote the $n \times n$
matrix obtained by replacing each entry $A_{ij}$ of $A$ by
$p(A_{ij})$; thus $A^{[k]} = [x^k]A$. Let $P(x) = x^n + a_{n-1}x^{n-1} +$
$\cdots + a_0$ denote the characteristic polynomial of $A$. By the Cayley-Hamilton theorem,

Thus each entry of $A$ is a root of the polynomial $xp(x)$.
Now suppose $m \geq n+1$. Then

since each entry of $A$ is a root of $x^{m+1-n}P(x)$. On the other hand,

Therefore if $A^k = A^{[k]}$ for $m+1-n \le k \le m$, then $A^{m+1} = A^{[m+1]}$. The desired result follows by induction on $m$.

Remark. David Feldman points out that the result is
best possible in the following sense: there exist examples of $n \times n$ matrices $A$ for which $A^k = A^{[k]}$ for
$k = 1, \dots, n$ but $A^{n+1} \neq A^{[n+1]}$.
