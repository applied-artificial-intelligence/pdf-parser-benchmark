# Solutions to the 71st William Lowell Putnam Mathematical Competition

# Saturday, December 4, 2010

Kiran Kedlaya and Lenny Ng

A-1 The largest such $k$ is $\lfloor \frac{n+1}{2} \rfloor = \lceil \frac{n}{2} \rceil$. For n even, this value
is achieved by the partition

for $n$ odd, it is achieved by the partition

One way to see that this is optimal is to note that the common sum can never be less than $n$, since $n$ itself belongs to one of the boxes. This implies that $k \leq (1 + \cdots + n)/n = (n + 1)/2$. Another argument is that if $k > (n + 1)/2$, then there would have to be two boxes with one number each (by the pigeonhole principle), but such boxes could not have the same sum.

Remark.A much subtler question would be to find the smallest $k$ (as a function of $n$ ）for which no such arrangement exists.

A-2 The only such functions are those of the form $f(x) =$ $cx + d$ for some real numbers $c, d$ (for which the property is obviously satisfied). To see this, suppose that $f$ has the desired property. Then for any $x \in \mathbb{R}$,

Consequently, $f ^ { \prime } ( x + 1 ) = f ^ { \prime } ( x ) $

Define the function $g: \mathbb{R} \to \mathbb{R}$ by $g(x) = f(x+1) - f(x)$, and put $c=g(0)$, $d=f(0)$. For all $x \in \mathbb{R}$, $g'(x) = f'(x+1) - f'(x) = 0$, so $g(x) = c$ identically, and $f'(x) = f(x+1) - f(x) = g(x) = c$, so $f(x)=cx+d$ identically as desired.

A-3 If $a = b = 0$, then the desired result holds trivially, so
we assume that at least one of $a,b$ is nonzero. Pick
any point $(a_0,b_0) \in \mathbb{R}^2$, and let $L$ be the line given by
the parametric equation $L(t) = (a_0,b_0) + (a,b)t$ for $t \in$
$\mathbb{R}$. By the chain rule and the given equation, we have
$\frac{d}{dt}(h \circ L) = h \circ L$. If we write $f = h \circ L : \mathbb{R} \to \mathbb{R}$, then
$f'(t) = f(t)$ for all $t$. It follows that $f(t) = Ce^t$ for some
constant $C$. Since $|f(t)| \le M$ for all $t$, we must have
$C = 0$. It follows that $h(a_0,b_0) = 0$; since $(a_0,b_0)$ was an arbitrary point, $h$ is identically 0 over all of $\mathbb{R}^2$.

A-4 Put

Write $n = 2^m k$ with $m$ a nonnegative integer and $k$ a positive odd integer. For any nonnegative integer $j$,

Since $10^n \geq n \geq 2^m \geq m+1$, $10^n$ is divisible by $2^n$ and
hence by $2^{m+1}$, and similarly $10^{10^n}$ is divisible by $2^{10^n}$
and hence by $2^{m+1}$. It follows that

Since $N \geq 10^{10^n} > 10^n + 1 \geq 10^{2^m} + 1$, it follows that $N$ is composite.

A-5 We start with three lemmas.

Lemma 1. If $ \mathbf{x}, \mathbf{y} \in G $ are nonzero orthogonal vectors, then $ \mathbf{x} * \mathbf{x} $ is parallel to $\mathbf{y}$.

Proof. Put $\mathbf{z} = \mathbf{x} \times \mathbf{y} \neq 0$, so that $\mathbf{x}, \mathbf{y}$, and $\mathbf{z} = \mathbf{x} \times \mathbf{y}$ are nonzero and mutually orthogonal. Then $\mathbf{w} = \mathbf{x} \times \mathbf{z} \neq 0$, so $\mathbf{w} = \mathbf{x} \times \mathbf{z}$ is nonzero and orthogonal to $\mathbf{x}$ and $\mathbf{z}$. However, if $(\mathbf{x} * \mathbf{x}) \times \mathbf{y} \neq 0$, then $\mathbf{w} = \mathbf{x} * (\mathbf{x} * \mathbf{y}) = (\mathbf{x} * \mathbf{x}) * \mathbf{y} = (\mathbf{x} * \mathbf{x}) \times \mathbf{y}$ is also orthogonal to $\mathbf{y}$, a contradiction.    □

Lemma 2. If $\mathbf{x} \in G$ is nonzero, and there exists $\mathbf{y} \in G$ nonzero and orthogonal to $\mathbf{x}$, then $\mathbf{x} * \mathbf{x} = 0$.

Proof. Lemma 1 implies that $\mathbf{x} * \mathbf{x}$ is parallel to both $\mathbf{y}$ and $\mathbf{x} \times \mathbf{y}$, so it must be zero. $\square$

Lemma 3. If $\mathbf{x}, \mathbf{y} \in G$ commute, then $\mathbf{x} \times \mathbf{y} = 0.$

Proof. If $\mathbf{x} \times \mathbf{y} \neq 0$, then $\mathbf{y} \times \mathbf{x}$ is nonzero and distinct from $\mathbf{x} \times \mathbf{y}$. Consequently, $\mathbf{x} * \mathbf{y} = \mathbf{x} \times \mathbf{y}$ and $\mathbf{y} * \mathbf{x} = \mathbf{y} \times \mathbf{x} \neq \mathbf{x} * \mathbf{y}$.     □

We proceed now to the proof. Assume by way of contradiction that there exist $\mathbf{a}, \mathbf{b} \in G$ with $\mathbf{a} \times \mathbf{b} \neq 0$. Put
$\mathbf{c} = \mathbf{a} \times \mathbf{b} = \mathbf{a} * \mathbf{b}$, so that $\mathbf{a}, \mathbf{b}, \mathbf{c}$ are nonzero and linearly independent. Let $\mathbf{e}$ be the identity element of $G$.
Since $\mathbf{e}$ commutes with $\mathbf{a}, \mathbf{b}, \mathbf{c}$, by Lemma 3 we have
$\mathbf{e} \times \mathbf{a} = \mathbf{e} \times \mathbf{b} = \mathbf{e} \times \mathbf{c} = 0$. Since $\mathbf{a}, \mathbf{b}, \mathbf{c}$ span $\mathbb{R}^3$, $\mathbf{e} \times \mathbf{x} = 0$
for all $\mathbf{x} \in \mathbb{R}^3$, so $\mathbf{e} = 0$.

Since ${ \mathbf { b } } , { \mathbf { c } }$ and $\mathbf { b } \times \mathbf { c } = \mathbf { b } * \mathbf { c }$ are nonzero and mutually orthogonal, Lemma 2 implies

Hence $\mathbf{b} * \mathbf{c} = \mathbf{c} * \mathbf{b}$, contradicting Lemma 3 because $\mathbf{b} \times$
$\mathbf{c} \neq 0$. The desired result follows.

A-6 First solution. Note that the hypotheses on $f$ imply
that $f(x) > 0$ for all $x \in [0,+\infty)$, so the integrand is a continuous function of $f$ and the integral makes sense. Rewrite the integral as
