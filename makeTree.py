from sklearn import tree
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--train',
                        help="training set")
    parser.add_argument('-s', '--test',
                        help="validation set")
    parser.add_argument('-d', '--depth', type=int, default=4,
                        help="maximum tree depth")
    parser.add_argument('-o', '--output',
                        help="output prefix")
    args = parser.parse_args()

    # Train
    X_trn, Y_trn = getData(args.train)
    clf = tree.DecisionTreeClassifier(max_depth=args.depth)
    clf = clf.fit(X_trn,Y_trn)

    # Test
    X_tst,Y_tst = getData(args.test)
    Y_hat = clf.predict(X_tst)
    with open(args.output+".treeReport.txt",'w') as o:
        # Find error rates
        err = misclassificationRate(Y_tst,Y_hat)
        classes = classifications(Y_tst,Y_hat)
        # Write report on error rates
        o.write("Trained over:\t"+args.train+"\n")
        o.write("Maximum depth:\t"+str(args.depth)+"\n\n")
        o.write("Validated on:\t"+args.test+"\n")
        o.write("Overall error:\t"+str(err)+"\n")
        o.write("False positive rate:\t"+
                str(float(classes[(1,-1)])/(classes[(1,-1)]+classes[(1,1)]))
                +"\n")
        o.write("False negative rate:\t"+
                str(float(classes[(-1,1)])/(classes[(-1,1)]+classes[(-1,-1)]))
                +"\n\n")
        o.write("Tree stored in:\t"+
                args.output+".tree.pkl")

    from sklearn.externals import joblib
    joblib.dump(clf, args.output+".tree.pkl", compress=9)


    return

def getData(infile):
    with open(infile) as f:
        #skip header
        f.readline()
        #Get features
        X = [ map(float,line.strip().split("\t")[3:]) 
              for line in f ]
 
        #Get labels
        f.seek(0)
        f.readline()
        Y = [ int(line.split("\t")[2]) 
              for line in f ]
    return X,Y

def misclassificationRate(Y,Y_hat):
    errors = [ int(y!=y_hat) for (y,y_hat) in zip(Y,Y_hat) ]
    return float(sum(errors))/len(Y)

def classifications(Y,Y_hat):
    from collections import defaultdict
    guess = defaultdict(int)
    for (y,y_hat) in zip(Y,Y_hat):
        guess[(y,y_hat)] += 1
    return guess

if __name__ == '__main__':
    main()
