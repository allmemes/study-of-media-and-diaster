## Google Trends Data

The folder `google-trends-data` contains Google Trends data of three keywords: **derailment**, **vinyl chloride**, and **East Palestine**, each with its own folder. 
In each keyword folder, there are four subfolders: `geoMap`, `multiTimeline`, `relatedEntities`, and `relatedQueries`.

The data in this repository is from February 3, 2023 to March 6, 2023. Please note that some data is missing:

* vinyl chloride: multiTimeline (32), relatedQueries (1, 28, 29, 30, 32), relatedEntities (1, 30, 32).
* east Palestine: multiTimeline (32)
* derailment: multiTimeline (32)

### `geoMap` - Interest by subregion (metro)
See in which location your term was most popular during the specified time frame. It shows the keyword's interest by subregion (metro) on a scale of 0-100, with 100 being the most popular location and 0 indicating insufficient data.

### `multiTimeline` - Interest over time
Numbers represent search interest relative to the highest point on the chart for the given region and time. A value of 100 is the peak popularity for the term. A value of 50 means that the term is half as popular. A score of 0 means there was not enough data for this term.

### `relatedEntities` - Related topics
This folder contains data on related topics for each keyword. The data shows what users searched for in addition to the specified term, and can be viewed by the following metrics:

* Top: The most popular topics. Scores range from 100 (most commonly searched) to 50 (half as often as the most popular), and so on.
* Rising: Related topics with the biggest increase in search frequency since the last time period. Results marked "Breakout" had a tremendous increase, likely due to being new with few (if any) prior searches.

### `relatedQueries` - Related queries
 This folder contains data on topics related to the keyword. You can sort by the following metrics:
  * Top: The most popular search queries. Scoring is on a relative scale where a value of 100 is the most commonly searched query, 50 is a query searched half as often as the most popular query, and so on.
  * Rising: Queries with the biggest increase in search frequency since the last time period. Results marked "Breakout" had a tremendous increase, probably because these queries are new and had few (if any) prior searches.
