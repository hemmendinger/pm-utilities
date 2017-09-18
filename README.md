# GJOpen Utilities
http://github.com/hemmendinger/gjopen-utilities

Credentials: I figured it is least annoying to just login manually. 
Maybe will save the cookie in the future, but am avoiding any application state for now. 


## TODO: gjopen.py
Make consistent in code references to predictions/forecasts, lean toward "forecast"
Write test to compare # of forecasts retrieved to info under "Graphs & Stats" 
Save comments made along with forecasts


## TODO: analysis.py
Scoring functions using forecast probabilities
- must account for multiple forecasts per day, only count last one?
- should we sort by age or assume sorted? assume sorted for now but test if dates are ascending
 (reverse list easily with [x for x in reversed(list)] )
- calculate median brier scores for a question
- trying to handle data where forecasts made one 1 day are applicable until forecast changes, but seems complicated

Ordered categorical scoring rule
- http://training.goodjudgment.com/Ordered_Categorical_Scoring_Rule.pdf
