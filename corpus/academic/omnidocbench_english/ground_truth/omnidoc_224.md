Thus $A_k$ is positive definite. Its eigenvalues (not the same $\lambda_1$!) must be positive. Its determinant is their product, so all upper left determinants are positive.

If condition Ⅲ holds, so does condition Ⅳ: According to Section 4.4, the $k$ th pivot $d_k$ is the ratio of $\det A_k$ to $\det A_{k-1}$. If the determinants are all positive, so are the pivots.

If  condition Ⅳ holds, so does conditionⅠ: We are given positive pivots, and must deduce that $x^T A x > 0$. This is what we did in the 2 by 2 case, by completing the square. The pivots were the numbers outside the squares. To see how that happens for symmetric matrices of any size, we go back to elimination on a symmetric matrix: $A = LDL^T$.

Example 1. Positive pivots 2, $\frac{3}{2}$, and $\frac{4}{3}$:

I want to split $x^\mathrm{T}Ax$ into $x^\mathrm{T}LDL^\mathrm{T}x$:

So $x^{\mathrm{T}}Ax$ is a sum of squares with the pivots 2, $\frac{3}{2}$, and $\frac{4}{3}$ as coefficients:

Those positive pivots in $D$ multiply perfect squares to make $x^{\mathrm{T}}Ax$ positive. Thus condition Ⅳ implies condition Ⅰ, and the proof is complete.

It is beautiful that elimination and completing the square are actually the same. Elimination removes $x_1$ from all later equations. Similarly, the first square accounts for all terms in $x^{\mathrm{T}}Ax$ involving $x_1$. The sum of squares has the pivots outside. The multipliers $\ell_{ij}$ are inside! You can see the numbers $-\frac{1}{2}$ and $-\frac{2}{3}$ inside the squares in the example.

Every diagonal entry $a_{ii}$ must be positive. As we know from the examples, however, it is far from sufficient to look only at the diagonal entries.

The pivots $d_i$ are not to be confused with the eigenvalues. For a typical positive
definite matrix, they are two completely different sets of positive numbers, In our 3 by 3
example, probably the determinant test is the easiest:

Determinant test

The pivots are the ratios $d_1 = 2, d_2 = \frac{3}{2}, d_3 = \frac{4}{3}$. Ordinarily the eigenvalue test is the longest computation. For this $A$ we know the $\lambda$'s are all positive:

Eigenvalue test

Chapter 6 Positive Definite Matrices

354