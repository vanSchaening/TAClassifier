def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infile',
                        help="complete dataset")
    parser.add_argument('-o', '--output',
                        help="output prefix")
    parser.add_argument('-f', '--size', type=float, default=0.15,
                        help="fraction of points to withhold for testing")
    parser.add_argument('-b', '--balance', default=False,
                        help="Whether or not to balance the data")
    args = parser.parse_args()

    if args.balance:
        trnfile,tstfile = makeBalancedData(args.infile,args.size,args.output)
    else:
        trnfile,tstfile = makeDatasets(args.infile,args.size,args.output)

    return


# Partitions data into train and validate while making sure to keep the number
# of negative points equal to positive (assumes positive is smaller)
def makeBalancedData(infile,f,output):
    X = getData(infile)

    pos = sum([ int(data[2]==1) for data in X ])
    keep = int(pos*(1-f))

    # Get positive points for training and validating
    trnfile = output+".train.txt"
    tstfile = output+".test.txt"
    with open(trnfile,'w') as trn, open(tstfile,'w') as tst:
        # Write the positive points
        X_trn,X_tst = partition([data for data in X if data[2] > 0],
                                keep)
        trn.write(formatForOutput(X_trn))
        tst.write(formatForOutput(X_tst))

        # Write the negative points, count positive test points to 
        # keep it balanced
        max_neg = len(X_tst)
        X_trn,X_tst = partition([data for data in X if data[2] < 2],
                                keep)
        trn.write(formatForOutput(X_trn))
        tst.write(formatForOutput(X_tst[0:max_neg]))

    return trnfile, tstfile


def formatForOutput(X):
    return "\n".join(["\t".join([str(feature) for feature in data]) 
                      for data in X]) 


def partition(points,keep):
# Randomly choose |keep| points in a class
    from random import shuffle
    shuffle(points)
    points_trn = points[0:keep]
    points_tst = points[keep:]
    return points_trn, points_tst
    
def getData(infile):
    with open(infile) as f:
        #skip header
        f.readline()
        #Get features
        X = [ line.strip().split("\t") for line in f ]
        for sample in X:
            sample[2] = int(sample[2])
    return X


# Partitions the data into train and validate        
def makeDatasets(infile,fraction,output):
    with open(infile) as f:
        # Find the number of datapoints to keep for test set
        count = sum([1 for line in f])
        keep = int(count*fraction)
        f.seek(0,0)
        # For each line, generate a random number between 0 and count
        # if that number is smaller than keep, store in test
        # otherwise, store in validate
        trnfile = output+".train.txt"
        tstfile = output+".test.txt"
        with open(trnfile,'w') as trn, open(tstfile,'w') as tst:
            from random import randint
            for line in f:
                val = randint(0,count)
                if val <= keep:
                    tst.write(line)
                else:
                    trn.write(line)
    return trnfile,tstfile

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
