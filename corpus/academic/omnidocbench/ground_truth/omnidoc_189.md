**(d)**

*(e)*

(f) The LALR(1) parsing table is the same as the SLR(1) parsing table shown in (c).

# Exercise 5.10

We use similar language to that on page 210, with appropriate modifications:

The SLR(1) parsing algorithm. Let s be the current state whose number is at the top of the parsing stack. Then actions are defined as follows:

(1) If state s contains any item of the form $ A \to\alpha. X \beta $ ,where X is a terminal, and X is the next token in the input string, then the action is to remove the current input token and push onto the stack the number of the state containing the item $ A \to\alpha X. \beta $

Page 5

Chapter 5 Exercise Answers,

Compiler Construction: Principles and Practice

https://www.coursehero.com/file/23512560/ch5ans/