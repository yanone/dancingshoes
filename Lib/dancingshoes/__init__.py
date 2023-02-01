#!/usr/bin/python

"""

Dancing Shoes

Dancing Shoes is a Python library that provides
a friendly interface to create OpenType feature code
using simple instructions.

DEVELOPERS
Yanone

MORE INFO (AND DOCUMENTATION)
http://www.yanone.de/typedesign/code/dancingshoes/

LICENSE
Copyright (c) 2009, Yanone
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions
and the following disclaimer in the documentation and/or other materials provided with the distribution.
Neither the name of the RoboFab Developers nor the names of its contributors may be used to endorse
or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

import string, os, re, copy
from dancingshoes import opentypenames
import functools

__all__ = ['opentypenames', 'helpers']
__version__ = '0.1.4'


# Main class

class DancingShoes:
	def __init__(self, glyphnames, features):
		self.glyphnames = glyphnames # List of glyph names
		self.features = features # List four-digit feature name codes, in order preferred by the foundry/designer
		self.adjustments = [] # List of OpenType adjustments. This is the main list and will be filled later
		self.glyphgroups = CollectGlyphGroups(self.glyphnames) # Dict of groups. glyphgroups['.tosf'] = ['one.tosf', 'two.tosf', 'three.tosf' ...]
		self.classes = Ddict(dict) # Two dimensional array of classes.
		self.stylisticsetnames = {}
		self.runningnumber = 0
		
		self.infos = []
		self.warnings = []
		self.errors = []
		
		self.indent = '  '
		

	def Info(self, string):
		self.infos.append(string)

	def Infos(self):
		if self.infos:
			return 'INFORMATIONS:\n' + '\n'.join(self.infos)
		else:
			return None

	def Warning(self, string):
		self.warnings.append(string)

	def Warnings(self):
		if self.warnings:
			return 'WARNINGS:\n' + '\n'.join(self.warnings)
		else:
			return None

	def Error(self, string):
		self.errors.append(string)

	def Errors(self):
		if self.errors:
			return 'ERRORS:\n' + '\n'.join(self.errors)
		else:
			return None

	def RunningNumber(self):
		self.runningnumber += 1
		return self.runningnumber

	def Glyphs(self):
		'''
		Returns self.glyphnames
		'''
		return self.glyphnames


	def HasGlyphs(self, glyphslist):
		'''
		Check, if a list of glyphnames is present in the collection of glyphnames of this object.
		Return True if all submitted glyphs are present.
		'''

		if isinstance(glyphslist, str):
			if glyphslist in self.glyphnames:
				return True
				
		elif isinstance(glyphslist, list) or isinstance(glyphslist, tuple):
			present = 0
			for glyph in glyphslist:
				if glyph in self.glyphnames:
					present += 1


			if present == len(glyphslist):
				return True
			else:
				return False

	def Groups(self):
		'''
		Returns self.glyphgroups.keys()
		'''
		return list(self.glyphgroups.keys())


	def HasGroups(self, groupslist):
		'''
		Check, if a list of glyphnames is present in the collection of glyphnames of this object.
		Return True, if all submitted glyphs are present.
		'''
		if isinstance(groupslist, str):
			if groupslist in self.Groups():
				return True

		elif isinstance(groupslist, list) or isinstance(groupslist, tuple):
			present = 0
			for group in groupslist:
				if group in self.Groups():
					present += 1
			if present == len(groupslist):
				return True
			else:
				return False
		else:
			return False


	def HasClasses(self, classnames):
		"""\
		Return all classes from given list that are currently registered.
		"""

		classespresent = []
		
		if isinstance(classnames, str):
			if classnames in self.classes:
				classespresent.append(classnames)

		elif isinstance(classnames, list) or isinstance(classnames, tuple):

			for classname in classnames:
				if classname in self.classes:
					classespresent.append(classname)
			
		return classespresent


	def GlyphsInGroup(self, ending):
		'''
		Returns self.glyphgroups[ending]
		'''
		if ending in self.Groups():
			return self.glyphgroups[ending]
		else:
			return []


	def GroupHasGlyphs(self, ending, glyphslist):
		'''
		Returns True if all glyphs are present in group
		'''
		if ending in self.Groups():

			if isinstance(glyphslist, str):
				if glyphslist in self.GlyphsInGroup(ending):
					return True

			elif isinstance(glyphslist, list) or isinstance(glyphslist, tuple):
				present = 0
				for glyph in glyphslist:
					if glyph in self.GlyphsInGroup(ending):
						present += 1
				if present == len(glyphslist):
					return True
				else:
					return False
		else:
			return False


	def SortGSUBLookups(self, feature, reverse = False):
		'''
		Sort lookups of type 'feature' by number of source glyphs.
		This is to make sure that 'sub f f i' comes before 'sub f i'. In that case, reverse must be set to True.
		Example: shoes.SortGSUBLookups('liga', reverse=True)
		'''
		self.adjustments = sorted(self.adjustments, reverse=reverse, key=lambda v: len(v.source.split(' ')) if (v.feature == feature and v.type == 'GSUBLookup') else None)


	def SourceGlyphFromTarget(self, target):
		return os.path.splitext(target)[0]


	def UsedFeatures(self):
		'''
		Returns list of all four-digit feature code names that have been successfully registered so far.
		'''
		list = []
		for feature in self.features:
			for adjustment in self.adjustments:
				if feature == adjustment.feature and not adjustment.feature in list:
					list.append(adjustment.feature)
		return list


	def UsedClasses(self):
		'''
		Returns list of all classes that have been successfully registered so far.
		'''
		return list(self.classes.keys())


	def UsedScripts(self, feature, includedefault = True, includeforeign = True):
		'''
		Returns list of all scripts that have been registered for given feature.
		"includedefault" and "includeforeign" are switches to distinguish between adjustments that have
		been registered for a specific script/language or for all default scripts/languages(Used for the FDK version switch).
		'''
		list = []
		for adjustment in self.adjustments:
			if feature == adjustment.feature and not adjustment.script in list:
				if includedefault and adjustment.script == '__DEFAULT__':
					list.append(adjustment.script)
				if includeforeign and adjustment.script != '__DEFAULT__':
					list.append(adjustment.script)
		return list


	def UsedLanguages(self, feature, script, includedefault = True, includeforeign = True):
		'''	Returns list of all languages that have been registered for given feature and script.
		"includedefault" and "includeforeign" are switches to distinguish between adjustments that have
		been registered for a specific script/language or for all default scripts/languages(Used for the FDK version switch).
		'''
		list = []
		for adjustment in self.adjustments:
			if feature == adjustment.feature and script == adjustment.script and not adjustment.language in list:
				if includedefault and adjustment.language == '__DEFAULT__':
					list.append(adjustment.language)
				if includeforeign and adjustment.language != '__DEFAULT__':
					list.append(adjustment.language)
		return list


	def UsedLookups(self, feature, script, language):
		'''
		Returns list of all lookups that have been registered for given feature and script and language.
		'''
		list = []
		for adjustment in self.adjustments:
			if language == adjustment.language and feature == adjustment.feature and script == adjustment.script:
				if not adjustment.lookup in list:
					list.append(adjustment.lookup)
		return list


	def UsedLookupFlags(self, feature, script, language, lookup):
		'''	Returns list of all lookupflags that have been registered for given feature and script and language.
		'''
		lookupflagslist = {}
		for adjustment in self.adjustments:
			if feature == adjustment.feature and script == adjustment.script and language == adjustment.language and lookup == adjustment.lookup:
				lookupflagslist[adjustment.lookupflag] = 'used'
		return list(lookupflagslist.keys())


	def UsedAdjustments(self, feature, script, language, lookup, lookupflag):
		'''
		Returns list of all adjustments that have been registered for given feature and script and language.
		'''
		adjustments = []
		for adjustment in self.adjustments:
			if language == adjustment.language and feature == adjustment.feature and script == adjustment.script and lookup == adjustment.lookup and lookupflag == adjustment.lookupflag:
				adjustments.append(adjustment)
		return adjustments


	def UsedScriptsAndLanguages(self):
		'''
		Returns list of tuples of all script/language combinations that have been registered.
		'''
		languagesystems = []

		_scripts = []

		for adjustment in self.adjustments:
			if not (adjustment.script, adjustment.language) in languagesystems:
				language = adjustment.language
				language = language.replace("dflt", '__DEFAULT__')
				languagesystems.append((adjustment.script, language))
			if not adjustment.script in _scripts:
				_scripts.append(adjustment.script)

		# Add dflt/dflt and ltn/dflt
		if not ('__DEFAULT__', '__DEFAULT__') in languagesystems:
			languagesystems.append(('__DEFAULT__', '__DEFAULT__'))
		for script in _scripts:
			if not (script, '__DEFAULT__') in languagesystems:
				languagesystems.append((script, '__DEFAULT__'))

		languagesystems.sort(key=functools.cmp_to_key(LanguageSystemSort))
		return languagesystems


	## Add adjustments

	def AddFeatureLookup(self, feature, lookupfeature, script = None, language = None, lookupflag = None, comment = None, lookup = None):

		# Check if feature is present in main feature list
		if not feature in self.features:
			self.Warning('Attempting to add feature adjustment to feature "%s", but the feature is not present in your features list' % (feature))

		if not lookupfeature in self.UsedFeatures():
			self.Info('Attempting to add feature "%s" adjustment to feature "%s", but the feature is not in use (yet)' % (lookupfeature, feature))

		self.adjustments.append(FeatureLookup(feature, script, language, lookup, lookupflag, lookupfeature, comment))


	def AddSimpleSubstitutionFeature(self, feature, ending):

		if self.HasGroups([ending]):

			# Check if feature is present in main feature list
			if not feature in self.features:
				self.Warning('Attempting to add simple substitutions to feature "%s", but the feature is not present in your supplied features list' % (feature))

			self.AddEndingToBothClasses(feature, ending)
			
			source = '@' + feature + '_source'
			target = '@' + feature + '_target'

			if self.GlyphsInClass(source) and self.GlyphsInClass(target):
				self.AddSubstitution(feature, source, target)
		else:
			self.Info('Attempting to add simple substitution feature "%s", but group "%s" is missing in your glyph repertoire.' % (feature, ending))

	def AddIgnoreSubstitution(self, feature, sequence, script = None, language = None, lookupflag = None, comment = None, lookup = None):

		# source and target sequence code is checked for presence
		sequencestring = self.DeflateClassString(sequence)

		if self.HasGlyphs(sequencestring):

			# Check if feature is present in main feature list
			if not feature in self.features:
				self.Warning('Attempting to add substitution to feature "%s", but the feature is not present in your supplied features list' % (feature))

			self.adjustments.append(IgnoreGSUBLookup(feature, sequence, script, language, lookup, lookupflag, comment))
		else:
			self.Info('Attempting to add substitution glyph sequence to feature "%s", but glyphs from the sequence ("%s")are missing in your glyph repertoire.' % (feature, sequence))
			
	def AddSubstitution(self, feature, source, target, script = None, language = None, lookupflag = None, comment = None, lookup = None):

		# source and target sequence code is checked for presence
		sourcestring = self.DeflateClassString(source)
		targetstring = self.DeflateClassString(target)
#		if feature == 'ss02':
#			print type(sourcestring)
#			print targetstring

		if self.HasGlyphs(sourcestring) and self.HasGlyphs(targetstring):


			# Check if feature is present in main feature list
			if not feature in self.features:
				self.Warning('Attempting to add substitution to feature "%s", but the feature is not present in your supplied features list' % (feature))

			self.adjustments.append(GSUBLookup(feature, source, target, script, language, lookup, lookupflag, comment))
		else:
			self.Info('Attempting to add substitution glyph sequence to feature "%s", but glyphs from either the source ("%s") or the target ("%s") are missing in your glyph repertoire.' % (feature, source, target))


	#def AddDuplicateFeature(self, sourcefeature, targetfeature):
	#	self.AddFeatureLookup(targetfeature, '', '', '', sourcefeature, '')



	def AddSinglePositioning(self, feature, glyph, adjustment, script = None, language = None, lookupflag = None, comment = None, lookup = None):

		# Check if feature is present in main feature list
		if not feature in self.features:
			self.Warning('Attempting to add single positioning adjustment to feature "%s", but the feature is not present in your supplied features list' % (feature))

		if isinstance(adjustment, int) or isinstance(adjustment, str):
			adjustment = (int(adjustment), 0, 0, 0)
	
		if self.HasGlyphs(self.DeflateClassString(glyph)):
			self.adjustments.append(GPOSLookupType1(feature, glyph, adjustment, script, language, lookup, lookupflag, comment))


	def AddPairPositioning(self, feature, pair, adjustment, script = None, language = None, lookupflag = None, comment = None, lookup = None):

		# Check if feature is present in main feature list
		if not feature in self.features:
			self.Warning('Attempting to add pair positioning adjustment to feature "%s", but the feature is not present in your supplied features list' % (feature))

		if isinstance(adjustment, int) or isinstance(adjustment, str):
			adjustment = (int(adjustment), 0, 0, 0)
	
		if self.HasGlyphs(self.DeflateClassString(pair)):
			self.adjustments.append(GPOSLookupType2(feature, pair, adjustment, script, language, lookup, lookupflag, comment))


	## Classes

	def AddGlyphsToClass(self, classname, glyphnames):
		if not classname.startswith('@'):
			classname = '@' + classname
		if classname not in self.classes:
			self.classes[classname] = []
			
		if isinstance(glyphnames, str) or isinstance(glyphnames, int) or isinstance(glyphnames, str):
			if self.HasGlyphs([glyphnames]):
				self.classes[classname].append(glyphnames)
		elif isinstance(glyphnames, tuple) or isinstance(glyphnames, list):
			for glyphname in glyphnames:
				if self.HasGlyphs([glyphname]):
					self.classes[classname].append(glyphname)


	def AddEndingToBothClasses(self, feature, ending):
		if ending in self.Groups():
			for glyph in self.GlyphsInGroup(ending):
				if self.HasGlyphs([glyph, self.SourceGlyphFromTarget(glyph)]):
					self.AddGlyphsToClass(feature + '_source', [self.SourceGlyphFromTarget(glyph)] )
					self.AddGlyphsToClass(feature + '_target', [glyph])

	def DuplicateFeature(self, source, target):
		
		# Check, if target feature is already in use
		if target in self.UsedFeatures():
			self.Warning("Duplicate feature '" + source + "' as '" + target + "'. The target feature '" + target + "' already contains some adjustments. I appended the instructions of '" + source + "' to '" + target + "', but they should be completely separate.")

		newadjustments = []
		for adjustment in self.adjustments:
			if adjustment.feature == source:
				newadjustment = copy.copy(adjustment)
				newadjustment.feature = target
				newadjustments.append(newadjustment)
		self.adjustments.extend(newadjustments)
		

	def SetStylisticSetName(self, featurename, description):
		self.stylisticsetnames[featurename] = str(description)
		
				

	# NEW in 1.0.3, not yet documented
	def GlyphsInClass(self, classname):
		if classname in self.classes:
			return self.classes[classname]
		else:
			return []


	# NEW in 1.0.3, not yet documented
	def ClassHasGlyphs(self, classname, glyphnames):
		if classname in self.classes:
			if isinstance(glyphnames, str):
				if glyphnames in self.GlyphsInClass(classname):
					return True
			elif isinstance(glyphnames, tuple) or isinstance(glyphnames, list):
				present = 0
				for glyph in glyphnames:
					if glyph in self.GlyphsInClass(classname):
						present += 1
				if present == len(glyphnames):
					return True
				else:
					return False
		else:
			return False
		

	def DeflateClassString(self, string):
		'''
		Deflate string containing glyph names, groups or class names into a flat group of glyph names.
		[@fractionslashes @dnom_target] @numr_target'
		'''
		list = []
		string = string.replace("'", "")
		string = string.replace("[", "")
		string = string.replace("]", "")
		
		tokens = string.split(' ')
		
		for token in tokens:
			if token.startswith('@'): # is class, add members of class
				classname = token[1:]
				if classname in self.classes:
					list.extend(self.classes[classname])
			else:
				list.append(token)
		return list


	## Generate Feature Code

	def GetFDKCode(self, codeversion = None):
		'''
		Return feature code all in one string.
		Available codeversions so far:
		FDK2.3
		FDK2.5
		'''

		codeversion = GetFDKCodeVersion(codeversion)
		featurecode = []
	
		if codeversion == '2.3':
			defaultscript = 'dflt'
			defaultlanguage = 'dflt'
		elif codeversion == '2.5':
			defaultscript = 'DFLT'
			defaultlanguage = 'dflt'
	
		# Language System
		featurecode.append(self.GetFDKLanguageSystemCode(codeversion))


		# Classes
		featurecode.append(self.GetFDKClassesCode(codeversion))


		# Run through Features
		for feature in self.UsedFeatures():
			featurecode.append(self.GetFDKFeatureCode(feature, codeversion))


		return '\n'.join(featurecode)


	def GetFDKFeatureCode(self, feature, codeversion = None):
		'''
		Return feature code all in one string.
		Available codeversions so far:
		FDK2.3
		FDK2.5
		'''

		featurecode = []
	
		featurecode.append('feature %s {' % (feature))

		featurecode.append(self.GetFDKFeatureContent(feature, codeversion))

		featurecode.append('')
		featurecode.append('} %s;' % (feature))
		featurecode.append('')

		return '\n'.join(featurecode)


	def GetFDKFeatureContent(self, feature, codeversion = None):
		'''
		Return feature code all in one string.
		Available codeversions so far:
		FDK2.3
		FDK2.5
		'''

		codeversion = GetFDKCodeVersion(codeversion)
		featurecode = []
	
		if codeversion == '2.3':
			defaultscript = 'dflt'
			defaultlanguage = 'dflt'
		elif codeversion == '2.5':
			defaultscript = 'DFLT'
			defaultlanguage = 'dflt'


		featurecode.append('# %s' % (opentypenames.OTfeatures[feature]))
		featurecode.append('')


		# Stylistic Set names
		if float(codeversion) >= 2.5 and feature[0:2] == 'ss' and feature in self.stylisticsetnames:

			featurecode.append("  featureNames {")
			featurecode.append("    name 1 \"%s\";" % (self.stylisticsetnames[feature]))
			featurecode.append("    name 3 \"%s\";" % (self.stylisticsetnames[feature]))
			featurecode.append("  };")
			featurecode.append('')

		# Default adjustments
		
		usedscripts = self.UsedScripts(feature)
		usedlanguages = self.UsedLanguages(feature, '__DEFAULT__')
		
		# adjustment has more than one script
		# put out dflt/dflt looklups directly here without script/language tags, if FDK version is 2.5

		featurecode.extend(self.GetFDKLookupContent(feature, '__DEFAULT__', '__DEFAULT__', 0, codeversion))
			
		# put out all other scripts/languages, including dflt/dflt for 2.3	

		# Script
		if codeversion == "2.3":
			usedscripts = self.UsedScripts(feature)
			usedscripts.sort(key=functools.cmp_to_key(ScriptSort))
		else:
			usedscripts = self.UsedScripts(feature, False, True)
			usedscripts.sort(key=functools.cmp_to_key(ScriptSort))
		

		for script in usedscripts:
			featurecode.append('')
			featurecode.append('  # %s' % (opentypenames.OTscripts[TranslateScript(script, defaultscript)]))
			featurecode.append('  script %s;' % (TranslateScript(script, defaultscript)))

			# Language
			usedlanguages = self.UsedLanguages(feature, script)
			usedlanguages.sort(key=functools.cmp_to_key(LanguageSort))

			for language in usedlanguages:
				featurecode.append('    # %s' % (opentypenames.OTlanguages[TranslateLanguage(language, defaultlanguage)]))
				featurecode.append('    language %s;' % (TranslateLanguage(language, defaultlanguage)))

				featurecode.extend(self.GetFDKLookupContent(feature, script, language, 3, codeversion))
			
		return '\n'.join(featurecode)


	def GetFDKLookupContent(self, feature, script, language, indentlevel, codeversion):

		featurecode = []
		usedlookups = self.UsedLookups(feature, script, language)

		if len(usedlookups) == 1:
			featurecode.extend(self.GetFDKLookups(feature, script, language, usedlookups[0], indentlevel + 1, codeversion))
		
		else:


			# Lookups
			for lookupKey in usedlookups:

				for lookupCode in self.GetFDKLookups(feature, script, language, lookupKey, indentlevel + 1, codeversion):

#					print lookupKey, lookupCode[:100]
		
					if lookupKey == '__DEFAULT__':
						lookupname = "%s_%s" % (feature, self.RunningNumber())
					else:
						lookupname = "%s_%s_%s" % (feature, lookupKey, self.RunningNumber())

					featurecode.append('%slookup %s {' % (self.indent * indentlevel, lookupname))
					featurecode.append(lookupCode)
					featurecode.append('%s} %s;' % (self.indent * indentlevel, lookupname))
					featurecode.append('')

		return featurecode

	def GetFDKLookups(self, feature, script, language, lookup, indentlevel, codeversion):

		featurecode = []

		# Script
		if codeversion == "2.3":
			lookupflagjoiner = ', '
		else:
			lookupflagjoiner = ' '

		lookupflags = self.UsedLookupFlags(feature, script, language, lookup)

		for lookupflag in lookupflags:
			lookupcode = []

			if lookupflag == '__DEFAULT__':
				lookupcode.extend(FDKadjustmentcode(self.UsedAdjustments(feature, script, language, lookup, '__DEFAULT__'), indentlevel + 1))
			else:
				lookupcode.append('%slookupflag %s;' % (self.indent * indentlevel, lookupflagjoiner.join(lookupflag.split(','))))
				lookupcode.extend(FDKadjustmentcode(self.UsedAdjustments(feature, script, language, lookup, lookupflag), indentlevel + 1))
			featurecode.append('\n'.join(lookupcode))


		return featurecode




	def GetFDKClassesCode(self, codeversion = None, break_after_glyphnames = 5):
		'''
		Return classes code all in one string.
		'''

		codeversion = GetFDKCodeVersion(codeversion)
		featurecode = []
		
		if codeversion == '2.3':
			defaultscript = 'dflt'
			defaultlanguage = 'dflt'
		elif codeversion == '2.5':
			defaultscript = 'DFLT'
			defaultlanguage = 'dflt'
	

		# Classes

		classes = list(self.classes.keys())
		classes.sort()
		for classname in classes:
			if not classname.startswith('@'):
				classname = '@' + classname
			featurecode.append('%s = [' % (classname))
			current_class = self.classes[classname]
			num_glyphs = len(current_class)
			num_lines = num_glyphs // break_after_glyphnames
			featurecode.append('# %i glyph(s)' % num_glyphs)
			for i in range(num_lines):
				featurecode.append(' '.join(current_class[:break_after_glyphnames]))
				current_class = current_class[break_after_glyphnames:]
			if len(current_class) > 0:
				featurecode.append(' '.join(current_class))
			featurecode.append('];')
			featurecode.append('')


		featurecode.append('')
		return '\n'.join(featurecode) + '\n\n'


	def GetFDKLanguageSystemCode(self, codeversion = None):
		'''
		Return language system code all in one string.
		'''

		codeversion = GetFDKCodeVersion(codeversion)
		featurecode = []
		
		if codeversion == '2.3':
			defaultscript = 'dflt'
			defaultlanguage = 'dflt'
		elif codeversion == '2.5':
			defaultscript = 'DFLT'
			defaultlanguage = 'dflt'
	
		featurecode.append('# Dancing Shoes %s OpenType feature code generator by Yanone, Copyright 2009' % (__version__))
		featurecode.append('# Code generated for AFDKO version %s' % (codeversion))
		featurecode.append('')
		featurecode.append('')

		# Script, language systems		
		for script, language in self.UsedScriptsAndLanguages():
			featurecode.append('languagesystem %s %s; # %s, %s' % (TranslateScript(script, defaultscript), TranslateLanguage(language, defaultlanguage), opentypenames.OTscripts[TranslateScript(script, defaultscript)], opentypenames.OTlanguages[TranslateLanguage(language, defaultlanguage)]))

		featurecode.append('')
		featurecode.append('')

		featurecode.append('')
		return '\n'.join(featurecode) + '\n\n'



	
# Different Lookup types

# GSUB

class IgnoreGSUBLookup:
	def __init__(self, feature, sequence, script, language, lookup, lookupflag, comment):
		self.type = 'IgnoreGSUBLookup'
		self.feature = feature
		self.sequence = sequence
		self.comment = comment

		self.script = script
		if not self.script:
			self.script = '__DEFAULT__'
		self.language = language
		if not self.language:
			self.language = '__DEFAULT__'
		self.lookup = lookup
		if not self.lookup:
			self.lookup = '__DEFAULT__'
		self.lookupflag = lookupflag
		if not self.lookupflag:
			self.lookupflag = '__DEFAULT__'
	
	def __repr__(self):
		return '<IgnoreGSUBLookup %s %s %s>' % (self.feature, self.sequence)

class GSUBLookup:
	def __init__(self, feature, source, target, script, language, lookup, lookupflag, comment):
		self.type = 'GSUBLookup'
		self.feature = feature
		self.source = source
		self.target = target
		self.comment = comment

		self.script = script
		if not self.script:
			self.script = '__DEFAULT__'
		self.language = language
		if not self.language:
			self.language = '__DEFAULT__'
		self.lookup = lookup
		if not self.lookup:
			self.lookup = '__DEFAULT__'
		self.lookupflag = lookupflag
		if not self.lookupflag:
			self.lookupflag = '__DEFAULT__'
	
	def __repr__(self):
		return '<GSUBLookup %s %s %s>' % (self.feature, self.source, self.target)


class FeatureLookup: # AFDKO: feature smcp;
	def __init__(self, feature, script, language, lookup, lookupflag, lookupfeature, comment):
		self.type = 'FeatureLookup'
		self.feature = feature
		self.lookupfeature = lookupfeature
		self.comment = comment

		self.script = script
		if not self.script:
			self.script = '__DEFAULT__'
		self.language = language
		if not self.language:
			self.language = '__DEFAULT__'
		self.lookup = lookup
		if not self.lookup:
			self.lookup = '__DEFAULT__'
		self.lookupflag = lookupflag
		if not self.lookupflag:
			self.lookupflag = '__DEFAULT__'

# GPOS

class GPOSLookupType1:
	def __init__(self, feature, glyphs, adjustment, script, language, lookup, lookupflag, comment):
		self.type = 'GPOSLookupType1'
		self.feature = feature
		self.glyphs = glyphs
		self.adjustment = adjustment # four touple (n, n, n, n)
		self.comment = comment

		self.script = script
		if not self.script:
			self.script = '__DEFAULT__'
		self.language = language
		if not self.language:
			self.language = '__DEFAULT__'
		self.lookup = lookup
		if not self.lookup:
			self.lookup = '__DEFAULT__'
		self.lookupflag = lookupflag
		if not self.lookupflag:
			self.lookupflag = '__DEFAULT__'

class GPOSLookupType2:
	def __init__(self, feature, pair, adjustment, script, language, lookup, lookupflag, comment):
		self.type = 'GPOSLookupType2'
		self.feature = feature
		self.pair = pair
		self.adjustment = adjustment # four touple (n, n, n, n)
		self.comment = comment

		self.script = script
		if not self.script:
			self.script = '__DEFAULT__'
		self.language = language
		if not self.language:
			self.language = '__DEFAULT__'
		self.lookup = lookup
		if not self.lookup:
			self.lookup = '__DEFAULT__'
		self.lookupflag = lookupflag
		if not self.lookupflag:
			self.lookupflag = '__DEFAULT__'



# Helper functions

def CollectGlyphGroups(glyphnames):

	list = Ddict(dict)

	for glyphname in glyphnames:
		if '.' in glyphname: # has ending, but is no ligature
			ending = os.path.splitext(glyphname)[1]
			if ending not in list:
				list[ending] = []
			list[ending].append(glyphname)
	
	return list

# write lines of FDK feature code

def FDKadjustmentcode(adjustments, indentlevel):
	featurecode = []
	indent = '  '
	

	for adjustment in adjustments:
		if isinstance(adjustment, IgnoreGSUBLookup):
			comment = ''
			if adjustment.comment: comment = '# ' + adjustment.comment
			featurecode.append((indentlevel * indent) + 'ignore sub %s; %s' % (adjustment.sequence, comment))

		elif isinstance(adjustment, GSUBLookup):
			comment = ''
			if adjustment.comment: comment = '# ' + adjustment.comment
			featurecode.append((indentlevel * indent) + 'sub %s by %s; %s' % (adjustment.source, adjustment.target, comment))

		elif isinstance(adjustment, FeatureLookup):
			comment = ''
			if adjustment.comment: comment = '# ' + adjustment.comment
			featurecode.append((indentlevel * indent) + 'feature %s; %s' % (adjustment.lookupfeature, comment))

		elif isinstance(adjustment, GPOSLookupType1):
			comment = ''
			if adjustment.comment: comment = '# ' + adjustment.comment
			if adjustment.adjustment[1] == 0 and adjustment.adjustment[2] == 0 and adjustment.adjustment[3] == 0:
				adjustmentcode = adjustment.adjustment[0]
			else:
				adjustmentcode = '<%s %s %s %s>' % (adjustment.adjustment[0], adjustment.adjustment[1], adjustment.adjustment[2], adjustment.adjustment[3])
			featurecode.append((indentlevel * indent) + 'pos %s %s; %s' % (adjustment.glyphs, adjustmentcode, comment))

		elif isinstance(adjustment, GPOSLookupType2):
			comment = ''
			if adjustment.comment: comment = '# ' + adjustment.comment
			if adjustment.adjustment[1] == 0 and adjustment.adjustment[2] == 0 and adjustment.adjustment[3] == 0:
				adjustmentcode = adjustment.adjustment[0]
			else:
				adjustmentcode = '<%s %s %s %s>' % (adjustment.adjustment[0], adjustment.adjustment[1], adjustment.adjustment[2], adjustment.adjustment[3])
			featurecode.append((indentlevel * indent) + 'pos %s %s; %s' % (adjustment.pair, adjustmentcode, comment))
	
	return featurecode


def TranslateLanguage(language, defaultlanguage):
	return language.replace('__DEFAULT__', defaultlanguage)

def TranslateScript(script, defaultlanguage):
	return script.replace('__DEFAULT__', defaultlanguage)



class Ddict(dict):
    def __init__(self, default=None):
        self.default = default
       
    def __getitem__(self, key):
        if key not in self:
            self[key] = self.default()
        return dict.__getitem__(self, key)


def GetFDKCodeVersion(codeversion):
	if not codeversion:
		try:
			import FL
			codeversion = "2.3"
		except:
			codeversion = "2.5"
	
	return codeversion

def ScriptSort(a, b):
	if a == 'latn':
		return -1
	else:
		return 0

def LanguageSort(a, b):
	if a == '__DEFAULT__':
		return -1
	else:
		return 0

def LanguageSystemSort(a, b):
	if a[0] == '__DEFAULT__' and a[1] == '__DEFAULT__':
		return -1
	elif a[1] == '__DEFAULT__' and b[1] != '__DEFAULT__':
		return -1
	else:
		return 0

def intersect(a, b):
	return list(set(a) & set(b))