# adsabs-pyingest

A collection or python parsers, validators, and serializers for adsabs 
ingest pipeline.  For the time being all we have is simple stuff used to
ingest data into ADS Classic, but this is meant to grow and change in 
due time as our metadata models become more sophisticated.

We are now starting to implement parsers that can be used to ingest directly
into Solr (e.g. dubcore/arxiv).  See the repository ADS_Direct_Import for
an example of this application.

# Using parsers

There are several different classes of parser that can be used for different
content sources (JATS, Proceedings of Science website, Zenodo, etc.)  The
basic syntax for calling a parser is simple: create an instance of the
parser, and obtain the parsed output using the "parse" method of the
parser on the required input.

For example, the APS parser requires a file pointer to an 
APS-JATS format fulltext.xml file (see the subdirectories under
/proj/ads/fulltext/sources/downloads/cache/APS).  Such a file could be
parsed with:

'''
from pyingest.parsers.aps import APSJATSParser
infile = "data_directory/apsjats-doi-fulltext.xml"
parser = APSJATSParser()
with open(infile,'rU') as fp:
    output = parser.parse(fp)
'''

All parsers are designed to give output in a format that can be serialized
by pyingest.serializers.classic.Tagged() to create an output file in ADS
tagged format.  Most parsers will return a single document; the exception
is procsci.PoSParser, which returns a list of documents (which collectively
make a TOC-formatted entry when passed to the classic serializer element by
element).

# Maintainers

Alberto Accomazzi, Director, NASA ADS

Matthew Templeton, NASA ADS
