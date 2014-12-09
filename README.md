TAClassifier
============

### Featurize

Running the featurize script after cloning the repository will download the 
negative datasets, (the directory should contain the positive points from TADB),
generate all the feature values for each point and write them all to a single 
data file.

### Build trees

Build trees uses the output from the previous script to build decision trees, 
controlling for the following parameters:
1. Maximum tree depth
2. Cross-validation, determine K.
Resulting decision trees will be stored as Python .pkl objects	    

##### Build an ensemble of trees
Instead of building a single tree, we can use each of the data sets we created
for cross validation as a training set for a separate tree. Then, to make a 
prediction, we average the predictions of the trees in the ensemble. We chose 
to implement this approach because decision trees have very high variance, and 
their structure can vary greatly depending on the input data. Using an ensemble
attempts to correct for this issue.

##### Build a random forest
Similar to building an ensemble, a random forest makes a prediction by combining
the output of multiple trees. However, those trees are built by randomizing the 
first feature to split on.

### Train an SVM

### Apply classifier
It receives a dataset and a classifier in a .pkl, and returns a list of 
predictions. The dataset can be received as either 
1. A table of features 
2. A pair of fasta files, where an entry is in the same putative TA system as the
corresponding entry in the other
