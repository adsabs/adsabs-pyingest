from pyingest.parsers.adsfeedback import ADSFeedbackParser
from pyingest.serializers.classic import Tagged


infile = './feedback_test.json'

with open(infile,'r') as ff:
    data = ff.read()
    output = ADSFeedbackParser(data).parse()
    parser = Tagged()
    parser.write(output)
