*Fig. 2. The training matrix.*

as input 1 of the training matrix has six different values, six processing units are built. However, the actual value is represented by a string,which is not a suitable input type for the FANN. Thus,such values are converted to a stream of 0's and 1's .Table1 illustratesthe codification for the raw material family.

The prior codification is necessary because FANNs only handle values within the closed interval [0,1]. Therefore the actual input and output values that the net receives and obtains are 0's and 1's . This codification-decodification is done by the encoder class attached to the machine agent (see Fig. 5). Therefore, the FANN has six processing units in the input layer, which are in charge of dealing exclusively with the raw material family. The totality of discrete values contained in the input and output sets were

**Table 1 Codification of the raw material family set**

codified in a similar way. Tables 2-6 show the resultant codification.

Consequently, the number of processing units in the input layer of the FANN equals the number of codified input values. For this case, 25 processing units in the input

O. Lopez-Ortega, I. Villar-Medina/Expert Systems with Applications 36 (2009) 2937-2946

2941