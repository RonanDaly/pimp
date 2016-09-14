library(profvis)
library(PiMP)
library(PiMPDB)

DATABASE_NAME='PiMP/tests/fixtures/test_database.db_fixture'
DATABASE_TYPE = 'sqlite'

source('PiMP/R/Pimp.exportToXML.R')
load('PiMP/tests/fixtures/Pimp.exportToXML.Robj_fixture')
db <- new("PiMPDB",
          dbuser='',
          dbpassword='',
          dbname=DATABASE_NAME,
          dbhost='',
          dbport=0,
          dbtype=DATABASE_TYPE
)
l = profvis(Pimp.exportToXML(id=analysis.id, raw.data=raw.data, identification=identification, toptables=toptables, pathway.stats=pathway.stats, identified.compounds.by.pathway=identified.compounds.by.pathway, db=db), interval=0.05, prof_output='.')
