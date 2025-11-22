columns $b_1, b_2, b_3$, the columns of $AB$ should be $Ab_1, Ab_2, Ab_3$!

Multiplication by columns

Our first requirement had to do with rows,and this one is concerned with columns. A third approach is to describe each individual entry in $A B$ and hope for the best. In fact,  there is only one possible rule,and I am not sure who discovered it. It makes everything work. It does not allow us to multiply every pair of matrices. If they are square, they must have the same size. If they are rectangular, they must not have the same shape; the number of columns in $A$ has to equal the number of rows in $B$ .Then $A$ can be multiplied into each column of $B$.

If $A$ is $m$ by $n$ ，and $B$ is $n$ by $p$ ,then multiplication is possible. The product $AB$ will be $m$ by $p$ .We now find the entry in row $i$ and column $j$ of $A B$.

1C  The  $i, j$ entry of $A B$  is the inner product of the $i$ th row of $A$ and the $j$ th column of $B$ .In Figure 1.7, the 3,2 entry of $A B$ comes from row 3 and column 2:

(6)

**Figure 1.7:** A 3 by 4 matrix $A$ times a 4 by 2 matrix $B$ is a 3 by 2 matrix $AB$.

Note.We write $A B$ when the matrices have nothing special to do with elimination. Our earlier example was $E A$ ,because of the elementary matrix $E$ . Later we have $P A$ ,or $L U$, or even $L D U$ . The rule for matrix multiplication stays the same.

# Example 1.

The entry 17 is $( 2 ) ( 1 ) + ( 3 ) ( 5 ) $, the inner product of the first row of $A$ and first column of $B$ . The entry 8 is $( 4 ) ( 2 ) + ( 0 ) ( - 1 )$ , from the second row and second column.

The third column is zero in $B$ , so it is zero in $AB$. $B$ consists of three columns side by side, and $A$ multiplies each column separately. Every column of $A B$ is a combination of the columns of $A $. Just as in a matrix-vector multiplication, the columns of $A$ are multiplied by the entries in $B$ .

## Chapter 1 Matrices and Gaussian Elimination
