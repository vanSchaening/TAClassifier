library(plyr)

features<-c("homology", "properties", "structure", "upalindromes", "essentiality")
class<-c("positive", "negative")
feature_names<-c("locus_id", "refseq", "class", 
                 "homology.toxin", "homology.antitoxin", 
                 "properties.gene1.pi", "properties.gene2.pi", "properties.gene1.weight", "properties.gene2.weight", 
                 "structure.gene1.length", "structure.gene2.length", "structure.distance", "structure.overlap",
                 "upalindromes.length", "upalindromes.distance", 
                 "essentiality.toxin", "essentiality.antitoxin")

import_by_refseq_and_class <- function(refseq, class) {
  filenames<-lapply(features, function(feature) paste(refseq, class, "features", feature, "txt", sep="."))
  tables<-llply(filenames, read.table)
  data<-Reduce(function(x, y) merge(x, y, by=1), tables)
  colnames(data)<-feature_names[c(1,4:length(feature_names))]
  data$class<-if(class=="positive") 1 else -1
  data$refseq<-refseq
  data<-data[feature_names]  
  return(data)
}

import_by_refseq <- function(refseq) {
  data<-lapply(classes, function(class) import_by_refseq_and_class(refseq, class))
  return(Reduce(rbind, data))
}

refseq<-"NC_011060"
data<-import_by_refseq(refseq)


