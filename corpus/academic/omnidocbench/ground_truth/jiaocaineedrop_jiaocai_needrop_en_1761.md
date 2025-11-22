例4：已知数列 $ \left \{ a_{n} \right \} $满足 $ a_{1}=2 $ $ a_{n+1}=2\Bigg(1+\frac{1}{n}\Bigg)^{2}a_{n} $ $ n\in N_{+} $

\t（ 1 ）求证：数列 $ \left\{\frac{a_n}{n^2}\right\} $是等比数列，并求出数列 $ \{a_{n} \} $的通项公式
\t（ 2 ）设 $ c_n=\frac{n}{a_n} $ ，求证： $ c_{1}+c_{2}+\cdots+c_{n}<\frac{17}{24} $

解：（ 1 ） $ a_{n+1}=2\Bigg(1+\frac{1}{n}\Bigg)^{2}a_{n}=2\cdot\frac{\left(n+1\right)^{2}}{n^{2}}a_{n} $
$ \therefore\frac{a_{n+1}}{\left(n+1\right)^2}=2\cdot\frac{a_n}{n^2} $ $ \therefore\left\{\frac{a_n}{n^2}\right\} $是公比为 2 的等比数列
$ \therefore\frac{a_{n}}{n^{2}}=\left(\frac{a_{1}}{1^{2}}\right)\cdot2^{n-1}=2^{n} $
$ \therefore a_{n}=n^{2}\cdot2^{n} $

\t ( 2 )  思路： $ c_{n}=\frac{n}{a_{n}}=\frac{1}{n\cdot2^{n}} $ ，无法直接求和，所以考虑放缩成为可求和的通项公式 （ 不等号： < ），若要放缩为裂项相消的形式，那么需要构造出 “顺序同构” 的特点。观察分母中有n，故分子分母通乘以 ( n - 1 ) ，再进行放缩调整为裂项相消形式。

解： $ c_{n}={\frac{n}{a_{n}}}={\frac{1}{n\cdot2^{n}}}={\frac{n\!-\!1}{n{\big(}n-1{\big)}2^{n}}} $
而 $ {\frac{1}{\left(n-1\right)2^{n-1}}}\!-\!{\frac{1}{n\cdot2^{n}}}\!=\!{\frac{2n\!-\!\left(n\!-\!1\right)}{n\!\left(n\!-\!1\right)2^{n}}}\!=\!{\frac{n\!+\!1}{n\!\left(n\!-\!1\right)2^{n}}} $
所以 $ c_{n}=\frac{n\!-\!1}{n\big(n\!-\!1\big)2^{n}}<\frac{n\!+\!1}{n\big(n\!-\!1\big)2^{n}}=\frac{1}{\big(n\!-\!1\big)2^{n\!-\!1}}-\frac{1}{n\!\cdot\!2^{n}}\big(n\!\geq\!2\big) $
$ \begin{array} {c} {{{c_{1}+c_{2}+\cdots+c_{n} < c_{1}+c_{2}+c_{3}+\left( \frac{1} {3 \cdot2^{3}}-\frac{1} {4 \cdot2^{4}}+\frac{1} {4 \cdot2^{4}}-\frac{1} {5 \cdot2^{5}}+\cdots+\frac{1} {\bigl( n-1 \bigr) 2^{n-1}}-\frac{1} {n \cdot2^{n}} \right)}}} \\ {{{=\frac{1} {2}+\frac{1} {8}+\frac{1} {2 4}+\frac{1} {2 4}-\frac{1} {n \cdot2^{n}}=\frac{1 7} {2 4}-\frac{1} {n \cdot2^{n}} < \frac{1 7} {2 4} \qquad( n > 3 )}}} \\ \end{array} $
$ \because c_{n} > 0 $ $ \therefore c_{1}<c_{1}+c_{2}<c_{1}+c_{2}+c_{3}={\frac{16}{24}}<{\frac{17}{24}} $

小炼有话说：（ 1 ）本题先确定放缩的类型，向裂项相消放缩，从而按 “依序同构” 的目标进

## 【 微信公众号：墨尘的数学笔记 】
