# twitter-d3
your twitter **private** account stalker.

> :warning: This program violates twitter robots.txt policy, since twitter disallows every crawling behavior except for those from googlebot.
> Following robots.txt is not mandatory, but you should keep in mind that all your behavior is against the policy of twitter, so use the script at your own risk. 

You can use this script in public account as well, but the key point of this script is that it is for the private account user activity pattern configurations.

## Usage
```
python3 main.py [-set_interval INTERVAL] twitter_id

positional arguments:
    twitter_id           twitter id (without @)

optional arguments:
    -h, --help          help
    -set_interval INTERVAL, -s INTERVAL
                        polling interval(default: 60s)

```
the output will be:
```
Total Tweet : 1324
Total Media : 332
Total Fav(Likes) : 3521

...(after the polling interval(default:60s))

Total Tweet : 1326 (+2 in last 60s)
Total Media : 333 (+1 in last 60s)
Total Fav(Likes) : 3521 (+0 in last 60s)

...and goes on...

```

## Example
```
python3 main.py -set_interval 600 bluehousekorea
```
600s means 10 mins

## Further Description
This script will be used in visualization for user activity time: See further information in my application.