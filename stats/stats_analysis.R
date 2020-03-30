# store extracted statictics in a dataframe
df<-read.csv('lpr2Rmann-whitney.csv',header = TRUE, sep = ",", dec='.')

# inspect the contents
head(df)
colnames(df)

# collect stats
summary(df)

# access columns and run the test
x=df$learner
y=df$ru_reference
wilcox.test(x,y, paired = FALSE)

# get a visual confirmation of numeric results
boxplot(df$learner,df$ru_reference,names=c("learner","ru_reference"))

# are the frequencies in targets correlated with the frequencies of the same items their sources? It does not necessarily mean that the latter trigger the translationese.
cor.test(df$profST, df$prof, method="kendall", alternative='g', exact=TRUE)

# calculating probabilities from z-scores
# (A z-score indicates how many steps an observation is from the mean)

# to find a probability of an observation less than a given with a particular z-score pass that z-score (here, =1) to
pnorm(1)

# for probabilities greater than a instance with a particular z-score (1)
1-pnorm(1)
