For linear programming, the important alternatives come when the constraints are inequalities. When is the feasible set empty (no $x$)？

**8J**   $Ax \ge b$ has a solution $x \ge 0$  or there is a $y \le 0$ with $yA \ge 0$ and $yb < 0$.

Proof. The slack variables $w = Ax - b$ change $Ax \geq b$ into an equation. Use 8I:

First alternative

Second alternative

It is this result that leads to a “nonconstructive proof" of the duality theorem.

# Problem Set 8.3

1. What is the dual of the following problem: Minimize $x_1 + x_2$, subject to $x_1 \ge 0$,
$x_2 \ge 0$, $2x_1 \ge 4$, $x_1 + 3x_2 \ge 11$? Find the solution to both this problem and its dual,
and verify that minimum equals maximum.
2. What is the dual of the following problem: Maximize $y_2$ subject to $y_1 \ge 0, y_2 \ge 0$,
$y_1 + y_2 \le 3$? Solve both this problem and its dual.
3. Suppose $A$ is the identity matrix (so that $m = n$), and the vectors $b$ and $c$ are nonnegative. Explain why $x^* = b$ is optimal in the minimum problem, find $y^*$ in the maximum problem, and verify that the two values are the same. If the first component of $b$ is negative, what are $x^*$ and $y^*$?
4. Construct a 1 by 1 example in which $A x \geq b, x \geq 0$ is unfeasible, and the dual problem is unbounded.
5. Starting with the 2 by 2 matrix $A = \begin{bmatrix} 1 & 0 \\ 0 & -1 \end{bmatrix}$, choose $b$ and $c$ so that both of the feasible sets $Ax \ge b, x \ge 0$ and $yA \le c, y \ge 0$ are empty.
6. If all entries of $A, b$, and $c$ are positive, show that both the primal and the dual are feasible.
7. Show that $x = ( 1 , 1 , 1 , 0 )$ and $y = ( 1 , 1 , 0 , 1 )$ are feasible in the primal and dual, with

Then, after computing $cx$ and $yb$, explain how you know they are optimal.

Chapter 8 Linear Programming and Game Theory

442