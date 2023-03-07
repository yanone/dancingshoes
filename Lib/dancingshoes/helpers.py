#!/usr/bin/python

import re, os
# input files
import csv

# read simple substitutions from a comma-delimited, quote-embraced CSV file
def SubstitutionsFromCSV(path):

	list = []
	with open(path, 'r') as csvfile:
		csvreader = csv.reader(csvfile)
		for row in csvreader:
#			print row
			if row[0] and row[1] and row[2]: # first three fields (feature, source and target) are required
				list.append(row)
	return list



def GlyphNamesFromFontLabFont(f):
	return [g.name for g in f.glyphs]

def GlyphNamesFromGlyphsFont(f):
	return [g.name for g in f.glyphs if g.export]

def GlyphNamesFromRoboFabFont(f):
	if hasattr(f, "glyphOrder"):
		return f.glyphOrder
	return list(f.keys())


def AssignFeatureCodeToFontLabFont(f, shoes):
	try:
		import FL
	except:
		shoes.Error("You're not within FontLab.")

	f.features.clean() # clean all previous features first
	for feature in shoes.UsedFeatures():
		f.features.append(FL.Feature(feature, shoes.GetFDKFeatureCode(feature)))
	f.ot_classes = shoes.GetFDKClassesCode() + shoes.GetFDKLanguageSystemCode()
	f.modified = 1
	FL.fl.UpdateFont()

def AssignFeatureCodeToGlyphsFont(f, shoes):
	
	from GlyphsApp import GSClass, GSFeature, GSFeaturePrefix
	
	while len(f.classes) > 0:
		del(f.classes[0])
	
	while len(f.features) > 0:
		del(f.features[0])

	while len(f.featurePrefixes) > 0:
		del(f.featurePrefixes[0])

	for feature in shoes.UsedFeatures():
		Feature = GSFeature()
		Feature.name = feature
		Feature.automatic = False # The Feature will not be removed on the next autogenerate run.
		Feature.code = shoes.GetFDKFeatureContent(feature)
		f.features.append(Feature)

	usedclasses = shoes.UsedClasses()
	usedclasses.sort()
	for otclass in usedclasses:
		newClass = GSClass()
		newClass.name = otclass.replace('@', '')
		newClass.code = '\n'.join(shoes.GlyphsInClass(otclass))
		newClass.automatic = False # The Class will not be removed on the next autogenerate run.
		f.classes.append(newClass)
		
	# Language systems
	aClass = GSFeaturePrefix()
	aClass.code = shoes.GetFDKLanguageSystemCode()
	aClass.name = "Languagesystems"
	f.featurePrefixes.append(aClass)

	for name, code in shoes.prefixes:
		Feature = GSFeaturePrefix()
		Feature.name = name
		Feature.automatic = False # The Feature will not be removed on the next autogenerate run.
		Feature.code = code
		f.featurePrefixes.append(Feature)

def AssignFeatureCodeToRoboFabFont(f, shoes):
	f.features.text = shoes.GetFDKCode()
	
def unquote(string):
	regex = re.search('"(.+)"', string)
	if regex:
		if not regex.group(1).startswith('#'): # cancel out comments
			return regex.group(1)
		else:
			return ''
	else: return ''

