def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infile',
                        help="complete dataset")
    parser.add_argument('-o', '--output',
                        help="output prefix")
    parser.add_argument('-s', '--species',
                        help="ID of species to remove")
    args = parser.parse_args()

    train,test = makeDatasets(args.infile, args.output, args.species)
    return

def makeDatasets(infile,prefix,species):
    # Make filenames
    train = prefix+".without_"+species+".train.txt"
    test  = prefix+".without_"+species+".test.txt"
    with open(infile) as f, open(train,'w') as trn, open(test,'w') as tst:
        for line in f:
            if line.startswith("#"):
                continue
            fields = line.strip().split("\t")
            if fields[1] == species:
                tst.write(line)
            else:
                trn.write(line)
    return train,test

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
