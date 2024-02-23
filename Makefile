reqs:
	pip install -r requirements.txt

run: 
	lsof -i :9000 | awk 'NR!=1 {print $$2}' | xargs -r kill -9
	python3 run.py


# uvicorn main:app --reload	
	