# store extracted statictics in a dataframe
df_bad<-read.table(file = '/home/u2/proj/parcorp/stats/tables/ud_stats_bad.tsv', sep = '\t', header = TRUE)
df_good<-read.table(file = '/home/u2/proj/parcorp/stats/tables/ud_stats_good.tsv', sep = '\t', header = TRUE)

# inspect the contents
head(df_bad)
colnames(df_good)

# collect stats
summary(df_bad)
 
# access columns and run the Wilcoson signed rank test
# see explanation of UD relations: https://universaldependencies.org/u/dep/index.html
# acl = adjectival clause
x=df_good$acl
y=df_bad$acl
wilcox.test(x,y, paired = FALSE)

# get a visual confirmation of numeric results
boxplot(df_good$acl,df_bad$acl,names=c("acl_good","acl_bad"))

# are the frequencies for aux.pass and nsubj.pass correlated (as you would expect)?
cor.test(df_good$aux.pass, df_bad$nsubj.pass, method="kendall", alternative='g', exact=TRUE)

