Multi-Factorial Experiments
===========================

A word about terminology
------------------------
An Attribute is a discrete level. A Group is a grouping of attributes; what might be called a discrete factor.


Front End

Django

fileupload
----------
 - ```views.py```



Database
--------
fileupload
----------
Sample
 - id
 - project
 - name
 - type (fk to SampleTypeTable)


 SampleTypeTable
 - id
 - name (QC, Sample, Blank, Standard)

SampleFile
 - sample (fk)
 - type (fk)
 - tic (fk curve)
 - file
 - fileName
 - slug
 - uploaded


 FileTypeTable
  - id
  - name
  - polarity (string)
  - msLevel (int)
  - format (string)

groups
------
Remove TicFile, TicGroup, ProjfileAttribute

experiments
-----------
Comparison
 - control (attribute) many-to-many
 - case (attribute) many-to-many


Migrations

R
==
 - ```runPimp.R```
 - ```runPipeline.R```
 - ```Pimp.processRawDAta```
 - ```Pimp.statistics.differential```
 - ```Pimp.statistics.pca```
 - ```Pimp.identify.metabolites```
 - ```Pimp.combine```
