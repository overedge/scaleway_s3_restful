<p align="center">
  <img src="https://raw.githubusercontent.com/overedge/scaleway_s3_restful/master/scaleway.png?centerme">
</p>

## HOW TO RUN
```
	docker-compose up
	python3 api.py
```

## ENDPOINTS
| ENDPOINT                | Second Header       |
| ------------------------| --------------------|
| GET    /image           | Display list Images |
| GET    /image/<int:id>  | Display Image       |
| POST   /image           | Upload  Image       |
| DELETE /image/<int:id>  | Delete  Image       |

## SOME TESTS
```
curl -X POST -F "description=mojo" -F "image=@./scaleway.png" -F "name=42" 127.0.0.1:5000
curl -X POST -F "image=@./scaleway.png" -F "name=42" 127.0.0.1:5000
curl -X POST -F "image=@./scaleway.png" 127.0.0.1:5000
curl -X POST -F "description=mojo" 127.0.0.1:5000
curl -X POST -F "description=mojo" -F "image=@./scaleway.png" 127.0.0.1:5000
curl http://127.0.0.1:5000/image
curl http://127.0.0.1:5000/image/1
curl -X DELETE http://127.0.0.1:5000/image/1
```



