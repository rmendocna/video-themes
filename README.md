# video-themes

Demo of a video library using mongoDB GridFS storage. 
User can:

 1. upload a video
 
 2. issue a *thumbs up* or a *thumbs down* 

![index](imgs/index.png)

![Upload Video](imgs/new.png)


Scores page shows the aggregations of videos by *thmes*, the number of videos in each theme and the score accoring to the rule:
    
    thumbs_up - (thumbs_dn / 2)

![Scores](imgs/scores.png)


