Mathematical Notation in PDFs
Mathematical Notation in PDFs
Academic papers and technical documents frequently contain mathematical
notation. Testing LaTeX math extraction is critical for evaluating parsers on
scientific content.
Inline Math
The quadratic formula is x = −b±
√
b2−4ac
2a
where a ̸= 0.
The normal distribution has probability density function f(x) =
1
σ
√
2πe−1
2(
x−µ
σ )
2
.
Einstein’s famous equation E = mc2 relates energy and mass.
Display Math
The Pythagorean theorem:
a2 + b2 = c2
Euler’s identity:
eiπ + 1 = 0
The fundamental theorem of calculus:
Z b
a
f ′(x) dx = f(b) −f(a)
Complex Equations
Matrix operations:
1

A =


a11
a12
a13
a21
a22
a23
a31
a32
a33


The determinant of a 3×3 matrix:
det(A) = a11(a22a33 −a23a32) −a12(a21a33 −a23a31) + a13(a21a32 −a22a31)
Greek Letters and Symbols
Common statistical notation uses Greek letters:
• Population mean: µ
• Population standard deviation: σ
• Sample mean: ¯x
• Correlation coefficient: ρ
• Probability: P(A ∩B) = P(A) · P(B|A)
Summations and Products
The sum of first n natural numbers:
n
X
i=1
i = n(n + 1)
2
The product notation:
n! =
n
Y
i=1
i
Limits and Derivatives
The definition of a derivative:
f ′(x) = lim
h→0
f(x + h) −f(x)
h
The limit definition of e:
e = lim
n→∞

1 + 1
n
n
2

Integrals
Double integral:
Z 1
0
Z 1
0
f(x, y) dy dx
Improper integral:
Z ∞
−∞
e−x2 dx = √π
Set Theory
Common set operations:
• Union: A ∪B
• Intersection: A ∩B
• Subset: A ⊆B
• Element of: x ∈A
• Empty set: ∅
Logic Notation
Logical operators:
• Conjunction: p ∧q
• Disjunction: p ∨q
• Negation: ¬p
• Implication: p =⇒q
• Equivalence: p ⇐⇒q
Conclusion
This document tests mathematical notation extraction including:
• Inline and display math
• Greek letters and symbols
• Fractions and radicals
• Summations and products
• Limits and derivatives
• Integrals
• Matrices
• Set theory and logic notation
3