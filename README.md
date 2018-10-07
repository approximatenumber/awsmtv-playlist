This is script that grabs youtube ids from awsmtv.com and adds them to YouTube playlist. It provides ability to watch videos from TV, because awsmtv.com doesn\`t 
support any device except desktop browsers.

### Running

```
docker run -d -it --rm \
 --name awsm \
 --cpus="2" \
 -v ${PWD}/app.py-oauth2.json:/app/app.py-oauth2.json \
 -v ${PWD}/client_secret.json:/app/client_secret.json \
 approximatenumber/awsmtv-playlist
```
