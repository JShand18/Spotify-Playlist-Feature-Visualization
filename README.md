# Spotify Playlist Feature Visualization
[WIP] Let's try this one more time

## Problem
My last attempt: [spotify-api-pipeline](https://github.com/JShand18/spotify-api-pipeline) proved troublesome when it came to using Lambda and Cloudwatch to facilitate the orchastration on the pipeline.
Two problems arose: 
1) Lambda only supports up to Python ~3.1, my project was built and dependent on Python 3.12
2) The payload sent to Lambda required all packages and the packages the depend on be sent in the payload as well, a problem that could be fixed but was not optimal for any future changes made to the extraction process.

## Solution
Orchestration via Airflow! Containers and images with Docker cause why not!


## Future Problems
1) Redshift is too expensive to have constantly running, so BigQuery, SnowflakeDB, or Databricks are alternatives that I should look into. But for now as I focus on the extraction process I'll keep Redshift in the infrastructure plans.
2) Being the aspiring data engineer that I am, I still want to remain true to software desigin pattern practices. So, I'll want to refactor the extraction process to follow a factory or strategy pattern. OOP in python? That surely wouldn't be a pain right? Surely it has to be better than a HTTP connections in Java.
3) It would be cool to compare the features of the playlists to the song that I am currently listening to, great excuse to stumble down Kafka streams.




## Credit
ABZ-Aaron's repo has provided me a verbose understanding of the infrastructure and tools to make this project possible, please consider giving a look: [Reddit–API–Pipeline](https://github.com/ABZ-Aaron/Reddit-API-Pipeline/tree/master)
