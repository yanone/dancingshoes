from dancingshoes.helpers import GlyphNamesFromRoboFabFont, AssignFeatureCodeToRoboFabFont
from myFP.features import MakeDancingShoes

# May Uncomment
#from robofab.world import CurrentFont

f = CurrentFont()

glyphnames = GlyphNamesFromRoboFabFont(f)

shoes = MakeDancingShoes(glyphnames)

AssignFeatureCodeToRoboFabFont(f, shoes)

# Verbose output
if shoes.Infos():
	print shoes.Infos()
if shoes.Warnings():
	print shoes.Warnings()
if shoes.Errors():
	print shoes.Errors()

print 'I enjoyed dancing with you...'

