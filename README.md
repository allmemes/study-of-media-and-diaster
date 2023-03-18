# What drives people's attention to disaster? A case study in Ohio Derailment

### 1. Setting

##### Investigation Time Period

2023/02/03 - 2023/03/08

### 2. Data Source

1. <u>Twitter</u> with keywords: has:geo (#Derailment OR "Vinyl chloride" OR "East Palestine")
2. <u>Google Trend</u> with keywords "Derailment", "EastPalestine", "VinylChloride"
3. <u>Google Earth API</u> with wind and temperature data
4. News (Manually or through Twitter)
5. Wikipedia
6. TikTok 

### 3. Methods

1. Set the label, can be the google trend/tweets/Wikipedia or some index taking all of them into consideration
2. Construct features
   - Toxic gases simulation
   - Tweets itself
   - News
   - Video on Tiktok
3. Aggregate the features and labels based on geology (county wise or state wise) and time series

### 4. Hypothesis

1. At the very beginning, people close to the local area are driven by our simulation result
2. Video on Tiktok can drive more people around the whole country
3. Everyone is interested in the disaster when there is some news actually coming out.
