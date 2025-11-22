Third solution: (by Richard Stanley) The cycle indicator of the symmetric group $S_n$ is defined by

where $c_i(\pi)$ is the number of cycles of $\pi$ of length $i$. Put

and

A standard argument in enumerative combinatorics (the Exponential Formula) gives

yielding

Expanding the right side as a Taylor series and comparing coefficients yields the desired result.

Fourth solution (sketch):(by David Savitt) We prove the identity of rational functions

by induction on $n$ ，which for $x = 1$ implies the desired result. (This can also be deduced as in the other solutions, but in this argument it is necessary to formulate the strong induction hypothesis.)

Let R ( n , x ) be the right hand side of the above equation. It is easy to verify that

since the sum telescopes. To prove the desired equality,
it suffices to show that the left hand side satisfies the
same recurrence. This follows because we can classify
each $\pi \in S_n$ as either fixing $n$, being an $n$-cycle, or having $n$ in an $l$ -cycle for one of $l = 2, \dots, n-1$; writing
the sum over these classes gives the desired recurrence.
