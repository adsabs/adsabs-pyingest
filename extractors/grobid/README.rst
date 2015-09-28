# Using grobid for structured extraction from PDF files

Some scripts and utilities to use grobid for extraction from pdfs.
For more information on grobid, see: https://github.com/kermitt2/grobid

## Dockerfile

Builds the latest version of grobid in a container, then runs it
in service mode (via grobid-server).  A RESTful API is then exposed
on port 8080. To build the service:
```
docker build -t grobid-server .
docker run -p 8081:8080 grobid-server
```

To test on a PDF file:
```
python process_pdf.py --server http://localhost:8081 astro-ph-0002105.pdf
```
This will create a file called astro-ph-0002105.pdf.xml


TODO:
* train new models for astro-specific content and have service accept models as input

