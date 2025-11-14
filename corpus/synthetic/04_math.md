# Mathematical Notation in PDFs

Academic papers and technical documents frequently contain mathematical notation. Testing LaTeX math extraction is critical for evaluating parsers on scientific content.

## Inline Math

The quadratic formula is $x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$ where $a \neq 0$.

The normal distribution has probability density function $f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{1}{2}\left(\frac{x-\mu}{\sigma}\right)^2}$.

Einstein's famous equation $E = mc^2$ relates energy and mass.

## Display Math

The Pythagorean theorem:

$$a^2 + b^2 = c^2$$

Euler's identity:

$$e^{i\pi} + 1 = 0$$

The fundamental theorem of calculus:

$$\int_a^b f'(x)\,dx = f(b) - f(a)$$

## Complex Equations

Matrix operations:

$$\mathbf{A} = \begin{pmatrix}
a_{11} & a_{12} & a_{13} \\
a_{21} & a_{22} & a_{23} \\
a_{31} & a_{32} & a_{33}
\end{pmatrix}$$

The determinant of a 3×3 matrix:

$$\det(\mathbf{A}) = a_{11}(a_{22}a_{33} - a_{23}a_{32}) - a_{12}(a_{21}a_{33} - a_{23}a_{31}) + a_{13}(a_{21}a_{32} - a_{22}a_{31})$$

## Greek Letters and Symbols

Common statistical notation uses Greek letters:

- Population mean: $\mu$
- Population standard deviation: $\sigma$
- Sample mean: $\bar{x}$
- Correlation coefficient: $\rho$
- Probability: $P(A \cap B) = P(A) \cdot P(B|A)$

## Summations and Products

The sum of first $n$ natural numbers:

$$\sum_{i=1}^{n} i = \frac{n(n+1)}{2}$$

The product notation:

$$n! = \prod_{i=1}^{n} i$$

## Limits and Derivatives

The definition of a derivative:

$$f'(x) = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}$$

The limit definition of $e$:

$$e = \lim_{n \to \infty} \left(1 + \frac{1}{n}\right)^n$$

## Integrals

Double integral:

$$\int_{0}^{1} \int_{0}^{1} f(x,y)\,dy\,dx$$

Improper integral:

$$\int_{-\infty}^{\infty} e^{-x^2}\,dx = \sqrt{\pi}$$

## Set Theory

Common set operations:

- Union: $A \cup B$
- Intersection: $A \cap B$
- Subset: $A \subseteq B$
- Element of: $x \in A$
- Empty set: $\emptyset$

## Logic Notation

Logical operators:

- Conjunction: $p \land q$
- Disjunction: $p \lor q$
- Negation: $\neg p$
- Implication: $p \implies q$
- Equivalence: $p \iff q$

## Conclusion

This document tests mathematical notation extraction including:

- Inline and display math
- Greek letters and symbols
- Fractions and radicals
- Summations and products
- Limits and derivatives
- Integrals
- Matrices
- Set theory and logic notation
