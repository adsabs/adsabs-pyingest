from pyingest.parsers.elsevier import ElsevierXmlParser

# infile = '/Users/mtempleton/0803/S0370269320301349.xml'
infile = '/Users/mtempleton/0803/S0370269320301453.xml'

lol = ElsevierXmlParser()

try:
    woot = lol.parse(infile)
except Exception as error:
    print("well, shit: %s", error)
else:
    print woot['doc:document']['ja:article']['ja:head']['ce:author-group']['ce:collaboration']['ce:author-group']
