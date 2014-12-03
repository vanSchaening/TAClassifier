def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infile',
                        help="complete dataset")
    parser.add_argument('-o', '--output',
                        help="output prefix")
    parser.add_argument('-f', '--size', type=float, default=0.15,
                        help="fraction of points to withhold for testing")
    args = parser.parse_args()

    trnfile,tstfile = makeDatasets(args.infile,args.size,args.output)
    return


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
                print val,keep
                if val <= keep:
                    tst.write(line)
                else:
                    trn.write(line)
    return trnfile,tstfile

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
