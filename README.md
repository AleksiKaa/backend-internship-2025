# Wolt 2025 Backend Engineering Internship assignment

This is my solution for the Wolt 2025 Backend Engineering Internship assignment. Setting things up and running the project is easy as first running:

```
python -m pip install -r requirements.txt
```
and then:
```
fastapi dev ./src/backend.py
```

in a terminal in the project root. You can then e.g. use ```curl``` at the endpoint specified in the assignment instructions. Note that ```fastapi``` defaults to port 8080.

The assignment also contains some unit tests. They can be run by simply running ```pytest``` in the project root.