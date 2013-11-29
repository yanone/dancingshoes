from dancingshoes.helpers import GlyphNamesFromFontLabFont, AssignFeatureCodeToFontLabFont
from myFP.features import MakeDancingShoes

f = fl.font
fl.output = ''

glyphnames = GlyphNamesFromFontLabFont(f)

shoes = MakeDancingShoes(glyphnames)

AssignFeatureCodeToFontLabFont(f, shoes)

# Verbose output
if shoes.Infos():
	print shoes.Infos()
if shoes.Warnings():
	print shoes.Warnings()
if shoes.Errors():
	print shoes.Errors()

print 'I enjoyed dancing with you...'
