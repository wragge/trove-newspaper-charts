#Trove newspaper charts

Script to produce some useful charts displaying the numbers of digitised newspaper articles available through Trove.

##Configuration

You'll need a [Trove API key](http://help.nla.gov.au/trove/building-with-trove/api) and a user name and key for [Plotly](http://plot.ly). Once you have these, add them to ```credentials-blank.py``` and rename the file to ```credentials.py```.

##Trove newspaper articles by year

```
create_totals_graph()
```

![Example chart](http://plot.ly/~wragge/303/trove-newspaper-articles-by-year.png)

[View live](http://plot.ly/~wragge/303/trove-newspaper-articles-by-year/)

##Trove newspaper articles by year for a given state

```
create_state_total_graph('vic')
```

![Example chart](http://plot.ly/~wragge/285/trove-newspaper-articles-victoria.png)

[View live](http://plot.ly/~wragge/285/trove-newspaper-articles-victoria/)

##Trove newspaper articles by year for all states

```
create_state_totals_graph()
```

![Example chart](http://plot.ly/~wragge/300/trove-newspaper-articles-by-state.png)

[View live](http://plot.ly/~wragge/300/trove-newspaper-articles-by-state/)