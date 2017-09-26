# GJOpen Utilities
http://github.com/hemmendinger/gjopen-utilities

Credentials: I figured it is least annoying to just login manually. 
Maybe will save the cookie in the future, but am avoiding any application state for now. 

## TODO: Timestamp handling
It might be necessary to explictly be setting a time as a UTC time,
or we may be accidentally comparing between UTC and a different timezone
Write tests to detect this mistake when possible

It could simplify things a lot if we just sorted lists by date, rather than defending against unsorted lists of dicts,
but "defending" seems to be convenient for the current workflow

## TODO: Implement state saving
Want to store/track previous data retrieved so we can just get most recent


## TODO: gjopen.py
Paging through forecasts
- Need total forecasts for knowing how many pages of forecasts to retrieve 
- Test to see if total forecasts = total forecasts in stats, they may not match up if only 1 forecasts per user is counted
- https://www.gjopen.com/comments/comments?id=558-how-much-crude-oil-will-libya-produce-in-september-2017-in-thousands-of-barrels-per-day-tb-d&commentable_id=558&commentable_type=Forecast%3A%3AQuestion&page=2

Make consistent in code references to predictions/forecasts, lean toward "forecast"
Write test to compare # of forecasts retrieved to info under "Graphs & Stats" 
Save comments made along with forecasts
Create functions that validate retrieved data, ensuring that it meets expectations

Automatically get question info along with ordering, still need user to assume if ordered scoring should be used
    

Don't assume that a user has one and only one unique prediction for a given timestamp, could be possible

## TODO: analysis.py
Scoring functions using forecast probabilities
- must account for multiple forecasts per day, only count last one?
- should we sort by age or assume sorted? assume sorted for now but test if dates are ascending
 (reverse list easily with [x for x in reversed(list)] )
- calculate median brier scores for a question
- trying to handle data where forecasts made one 1 day are applicable until forecast changes, but seems complicated

## Ideas
### Testing
Pick a closed question where the data is static and test against that
But we don't want to repeatedly download the page and test against it

## Incomplete Functions
### gjopen.py
filter_forecasts
carry_forward_my_forecasts

## References
Ordered categorical scoring rule, for questions with ordered ranges; providing extra points for closeness
- http://training.goodjudgment.com/Ordered_Categorical_Scoring_Rule.pdf
- https://www.gjopen.com/faq


