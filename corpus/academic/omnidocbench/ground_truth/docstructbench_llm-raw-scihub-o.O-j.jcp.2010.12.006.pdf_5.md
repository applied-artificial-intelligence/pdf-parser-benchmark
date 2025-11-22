where the difference operators $ \partial_{t}, $ $ \bar{\partial}_{t} $ are the discretization of $ \frac{\partial} {\partial t}, $ and the difference operators $ \partial_{x_{1}}, $ $ \overline{{{\partial}}}_{x_{1}} $ are the discretization of $ \frac{\partial} {\partial x_{1}}. $ .Via these notations and the properties of the difference operators, $ ^6 $ we present the statement of the local/global conservation laws for the different numerical methods.

# 3.1. Symplectic method for Maxwell's equations

The following method is constructed based on the method of lines, i.e. discretizing the Hamiltonian PDEs in space, then applying the symplectic method to the resulting Hamiltonian ODEs (see for example [6,22]). Later, we will show the method is also multisymplectic in the corresponding statement of multisymplecticity.

For Maxwell's equations in Hamiltonian form, we use the central finite difference in space (which is leapfrog discretization) and implicit midpoint rule (which is symplectic) in time, it is easy to show that the Hamiltonian formulations in (5) and (7) for Maxwell's equations reduce to the same discretized system,

(18)

where indices i,j, k denote spatial increments and index l denotes time increment, and matrices M, $ K_{1} $ ,... as in (10). We refer to this particular discretization as the symplectic method, though it is also multisymplectic.

The symplectic method (18) is second-order in space and time, and is unconditionally stable. Furthermore, this discrete system preserves two discretized global conservation laws: the first one is the discrete quadratic global conservation law based on(8),

(19)

The second discretized global conservation law for symplectic method is based on the helicity Hamiltonian functional (6)

(20)

where $ \widehat{\nabla} \times=R_{1} \partial_{x_{1}}+R_{2} \partial_{x_{2}}+R_{3} \partial_{x_{3}} $ . Furthermore, the scheme (18) is proved to be multisymplectic, since it preserves the following multisymplectic conservation law

(21)

Besides the global conservation laws, for the scheme (18) applied to Maxwell's equations, we also have the following local conservation laws based on (13)-(15):

The discrete quadratic conservation law is

(22)

The discrete energy conservation law is

(23)

The discrete momentum conservation law is

## Y. Sun, P.S.P. Tse/Journal of Computational Physics 230 (2011) 2076-2094

$ ^6 $ Let $ p_{i} $ and $ q_{i} $ are the functions at grid i, $ \partial, $ $ \overline{{{\partial}}} $ are the difference operators, then

$ \partial[ q_{i} p_{i} ]=q_{i+1} \partial p_{i}+\partial q_{i} p_{i}=\partial q_{i} p_{i+1}+q_{i} \partial p_{i}, $

$ \partial[ {\boldsymbol{q}}_{i+1} {\boldsymbol{p}}_{i} ]=\partial{\boldsymbol{q}}_{i+1} {\boldsymbol{p}}_{i+1}+{\boldsymbol{q}}_{i+1} \partial{\boldsymbol{p}}_{i}, $

$ \overline{{{{\partial}}}} [ q_{i} p_{i} ]=\overline{{{{\partial}}}} q_{i} p_{i+1}+q_{i-1} \overline{{{{\partial}}}} p_{i}=\overline{{{{\partial}}}} p_{i} q_{i+1}+p_{i-1} \overline{{{{\partial}}}} q_{i}, $

$ \overline{{{{\partial}}}} [ q_{i} p_{i+1} ]=q_{i+1} \overline{{{{\partial}}}} p_{i+1}+\overline{{{{\partial}}}} q_{i} p_{i}. $
