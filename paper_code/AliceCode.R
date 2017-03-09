GAM_use=function(variables){
  formula=" "
  for (i in variables)     ##c("temp","rh","pm2.5","mdiftemp","wind","rain")
  {formula=paste(formula,i,sep='')
  formula = paste(formula,") +s(" ,sep= " " )
  }
  formula = substring( formula,1,last = nchar(formula)-3)
  formula = paste( " GAMformula = gam( floor(ill) ~ s( " ,formula, sep= " " )
  formula = paste( formula,",family = poisson(),data =data)")
  eval(parse(text = formula))
  RSquare_adj = round(summary(GAMformula)$r.sq, 3)
  AIC = round(AIC(GAMformula),2)
  result<-c(RSquare_adj, AIC)
  return(result)
}

data = read.csv("/Users/liyizheng/data/tempdata/dataset.csv")
data = data[2:7]
ili_w=read.csv('/Users/liyizheng/data/tempdata/ili_week.csv')
li0=ili_w[1:157,]
ill=ili0[,3]
columns = colnames(data)
rsquare<-c()
aic <- c()
indexname<-c()
for (i in 1:length(columns)){
  subset_i  = combn(columns, i)
  col_length = ncol(subset_i)
  for (j in 1:col_length){
    result<-GAM_use(subset_i[,j])
    rsquare<-c(rsquare,result[1])
    aic<-c(aic,result[2])
    indexname<-c(indexname,paste(subset_i[,j],collapse = ','))
  }
}
dd=data.frame(indexname,rsquare,aic)
