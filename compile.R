# Compile features into a single data frame with tab-separated columns
# locus_id refseq class features...

# normalize data?

library(plyr)
library(ggplot2)

classes<-c("positive", "negative")
# enumerate all features
features<-c("homology", "properties", "structure", "upalindromes", "essentiality")
# enumerate all feature names here
feature_names<-c("locus_id", "refseq", "class", 
                 "homology.toxin", "homology.antitoxin", 
                 "properties.gene1.pi", "properties.gene2.pi", "properties.gene1.weight", "properties.gene2.weight", 
                 "structure.gene1.length", "structure.gene2.length", "structure.distance", "structure.overlap",
                 "upalindromes.length", "upalindromes.distance", 
                 "essentiality.toxin", "essentiality.antitoxin")

invert_colnames <- function() {
  inverted_colnames <- feature_names
  # swap gene1 and gene2
  inverted_colnames <- gsub('gene1', 'swap', inverted_colnames)
  inverted_colnames <- gsub('gene2', 'gene1', inverted_colnames)
  inverted_colnames <- gsub('swap', 'gene2', inverted_colnames)
  # swap toxin and antitoxin
  inverted_colnames <- gsub('.antitoxin', '.swap', inverted_colnames)
  inverted_colnames <- gsub('.toxin', '.antitoxin', inverted_colnames)
  inverted_colnames <- gsub('.swap', '.toxin', inverted_colnames)
  return(inverted_colnames)
}
inverted_colnames<-invert_colnames()

import_by_refseq_and_class <- function(refseq, class) {
  filenames<-lapply(features, function(feature) paste(paste(
    refseq, refseq, sep="/"), 
    class, "features", feature, "txt", sep="."))
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
  n = nrow(data)
  inverted<-data[data$class==-1,]
  colnames(inverted)<-inverted_colnames
  inverted<-inverted[feature_names]
  inverted$locus_id<-paste(inverted$locus_id, "i", sep="_")
  cat("Added", nrow(inverted), "inverted negatives.\n")
  return(rbind(data, inverted))
}

add_inverted_positives <- function(data) {
  n = nrow(data)
  inverted<-data[data$class==1,]
  colnames(inverted)<-inverted_colnames;
  inverted<-inverted[feature_names]
  inverted$locus_id<-paste(inverted$locus_id, "i", sep="_") 
  inverted$class<-(-1)
  cat("Added", nrow(inverted), "inverted negatives.\n")
  return(rbind(data, inverted))  
}

import_by_refseq <- function(refseq) {
  data<-lapply(classes, function(class) import_by_refseq_and_class(refseq, class))
  data<-Reduce(rbind, data)
  #data<-add_inverted_negatives(data)
  #data<-add_inverted_positives(data)
  data<-filter_by_structure(data)
  cat("refseq:", refseq, "positive:", sum(data$class==1), "negative:", sum(data$class==-1), '\n')
  return(data)
}

filter_by_structure <- function(data) {
  n = nrow(data)
  #max_overlap_positive = max(abs(data[data$class==1,]$structure.overlap))
  max_distance_positive = max(abs(data[data$class==1,]$structure.distance))
  #data<-data[abs(data$structure.overlap) < max_overlap_positive+1, ]
  data<-data[abs(data$structure.distance) < max_distance_positive+1, ]
  cat("Filtered", n-nrow(data), 'for structure.\n')
  return (data)
}

add_secondary_features <- function(data) {
  data$properties.ratio.pi = data$properties.gene1.pi/data$properties.gene2.pi
  data$essentiality.ratio = data$essentiality.antitoxin/data$essentiality.toxin
  data$essentiality.ratio[ is.nan(data$essentiality.ratio) ] <- 0
  data$essentiality.ratio[ is.infinite(data$essentiality.ratio) ] <- 0
  return(data)
}

normalize_data <- function(data) {
  return(data)
}

#args <- commandArgs(trailingOnly = TRUE) # use first argument as output file
#refseqs<-read.table(args[[1]])$V1
refseqs<-list.files('.', 'NC')
data<-Reduce(rbind, lapply(refseqs, import_by_refseq))
data<-add_secondary_features(data)
#write.table(data, file=args[[1]], quote=FALSE, sep="\t", row.names=FALSE)

#ggplot(data, aes(x=homology.antitoxin, group=as.factor(class), color=as.factor(class))) + geom_density()