from dancingshoes import DancingShoes
from dancingshoes.helpers import SubstitutionsFromCSV
import string

def MakeDancingShoes(glyphnames):
	
	# Your features, in the order you want them in the font
	features = ('aalt', 'locl', 'numr', 'dnom', 'frac', 'tnum', 'smcp', 'case', 'calt', 'liga', 'ss01', 'ss02', 'ss03')
	
	# Initialize DancingShoes object, hand over glyph names and default features
	shoes = DancingShoes(glyphnames, features)
	
	
	# Stylistic Sets
	for i in range(20):
		shoes.AddSimpleSubstitutionFeature('ss' + str(string.zfill(i, 2)), '.ss' + str(string.zfill(i, 2)))
	
	# Add direct substitutions
	directsubstitutions = (
		('smcp', '.sc'),
		('case', '.case'),
		('tnum', '.tf'),
		('ss01', '.ss01'),
		('ss02', '.ss02'),
		('ss03', '.ss03'),
		)
	for feature, ending in directsubstitutions:
		shoes.AddSimpleSubstitutionFeature(feature, ending)

	# Arabic
	if shoes.HasGroups(['.init']):
		shoes.AddEndingToBothClasses('init', '.init')
		shoes.AddSubstitution('init', "@init_source", "@init_target", 'arab', '', 'RightToLeft')


	# You can write contextual code for your script fonts using your own glyph name endings
	if shoes.HasGroups(['.initial', '.final']):
		# Add contextual substitution magic here
		for target in shoes.GlyphsInGroup('.initial'):
			shoes.AddGlyphsToClass('@initialcontext', ('a', 'b', 'c'))
			shoes.AddSubstitution('calt', "@initialcontext %s'" % (shoes.SourceGlyphFromTarget(target)), target)
	
	# You can theoretically write your own kern feature (which FontLab can also do for you upon font generation):
	shoes.AddPairPositioning('kern', 'T A', -30)
	shoes.AddPairPositioning('kern', 'uniFEAD uniFEEB', (-30, 0, -60, 0), 'arab', '', 'RightToLeft')

	# From CSV file
	csvfile = "../substitutions.csv"
	for feature, source, target, script, language, lookupflag, comment in SubstitutionsFromCSV(csvfile):
		shoes.AddSubstitution(feature, source, target, script, language, lookupflag, comment)
	
	# Uppercase Spacing
	uppercaseletters = ['A', 'B', 'C', 'D', 'E']
	for uppercaseletter in uppercaseletters:
		if shoes.HasGlyphs(uppercaseletter):
			shoes.AddGlyphsToClass('@uppercaseLetters', uppercaseletter)
	if shoes.HasClasses('@uppercaseLetters'):
		shoes.AddSinglePositioning('cpsp', '@uppercaseLetters', (5, 0, 10, 0))
	

	shoes.DuplicateFeature('hist', 'ss20')
	
	return shoes