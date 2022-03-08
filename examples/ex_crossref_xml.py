from pyingest.parsers.crossref import CrossrefXMLParser



infile = '10.1029::137gm01.xml'

with open(infile, 'r') as fi:
    data = fi.read()

try:
    lol = CrossrefXMLParser()
    woo = lol.parse(data)
except Exception as err:
    print('ohnoes: %s' % err)
else:
    print('yay: %s' % woo)
