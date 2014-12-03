# Compile features into a single data frame with tab-separated columns
# locus_id refseq class features...

library(plyr)

features<-c("homology", "properties", "structure", "upalindromes", "essentiality")
classes<-c("positive", "negative")
feature_names<-c("locus_id", "refseq", "class", 
                 "homology.toxin", "homology.antitoxin", 
                 "properties.gene1.pi", "properties.gene2.pi", "properties.gene1.weight", "properties.gene2.weight", 
                 "structure.gene1.length", "structure.gene2.length", "structure.distance", "structure.overlap",
                 "upalindromes.length", "upalindromes.distance", 
                 "essentiality.toxin", "essentiality.antitoxin")

import_by_refseq_and_class <- function(refseq, class) {
  filenames<-lapply(features, function(feature) paste(refseq, class, "features", feature, "txt", sep="."))
  tables<-llply(filenames, read.table)
 
  options(warn=-1)
  data<-Reduce(function(x, y) merge(x, y, by=1), tables)
  options(warn=1)
  
  colnames(data)<-feature_names[c(1,4:length(feature_names))]
  data$class<-if(class=="positive") 1 else -1
  data$refseq<-refseq
  data<-data[feature_names] # enforce order
  return(data)
}

add_inverted_negatives <- function(data) {
  inverted<-data[data$class==-1,]
  colnames(inverted)<-c("locus_id", "refseq", "class", 
                        "homology.antitoxin", "homology.toxin", 
                        "properties.gene2.pi", "properties.gene1.pi", "properties.gene2.weight", "properties.gene1.weight", 
                        "structure.gene2.length", "structure.gene1.length", "structure.distance", "structure.overlap",
                        "upalindromes.length", "upalindromes.distance", 
                        "essentiality.antitoxin", "essentiality.toxin")
  inverted<-inverted[feature_names]
  inverted$locus_id<-paste(inverted$locus_id, "i", sep="_")
  return(rbind(data, inverted))
}

add_inverted_positives <- function(data) {
  inverted<-data[data$class==1,]
  colnames(inverted)<-c("locus_id", "refseq", "class", 
                        "homology.antitoxin", "homology.toxin", 
                        "properties.gene2.pi", "properties.gene1.pi", "properties.gene2.weight", "properties.gene1.weight", 
                        "structure.gene2.length", "structure.gene1.length", "structure.distance", "structure.overlap",
                        "upalindromes.length", "upalindromes.distance", 
                        "essentiality.antitoxin", "essentiality.toxin")
  inverted<-inverted[feature_names]
  inverted$class<-1
  inverted$locus_id<-paste(inverted$locus_id, "i", sep="_") 
  return(rbind(data, inverted))  
}

import_by_refseq <- function(refseq) {
  data<-lapply(classes, function(class) import_by_refseq_and_class(refseq, class))
  return(Reduce(rbind, data))
}

args <- commandArgs(trailingOnly = TRUE) # use first argument as output file
refseq<-"NC_011060"
data<-import_by_refseq(refseq)
#data<-add_inverted_negatives(data)
#data<-add_inverted_positives(data)
write.table(data, file=args[[1]], quote=FALSE, sep="\t", row.names=FALSE)

