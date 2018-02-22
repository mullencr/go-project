GO_Interface v.0.0.1

==========[OVERVIEW]===========
>>> Introduction <<<
Gene Ontologies are the result of a movement by the Gene Ontology Consortium on behalf of bioinformaticists everywhere to standardize the way that we describe features in genomic databases. Until recently, different taxonomies have existed between projects, between species, and between specific research groups. The Gene Ontology Consortium has created a list of classifications that can be used to describe genetic features. This program allows you to upload a generated bgo file containing genetic feature annotation, adding it to a searchable database and pulling up meta-information about the Gene Ontology. A sample file with information on Mus Musculus (House Mouse) has been included for testing.

>>> Web Interface <<<
This software application consists of a single html page and a collection of perl scripts.
As certain tasks are performed by the user on the home page, the other perl scripts in
this folder are called, render the Home Page html, and then add on some information that
the user requested. These functions are:
	[HomePage.html]: The html page serves as an index, and the jumping off point for the user. 
	[read_in_terms.cgi]: This script receives a file upload from the user. The file upload
		will contain annotation information, pairing go_terms with genes from a test cluster.
		This script reads in the information and populates the database appropriately. After that,
		it returns the HomePage content along with some statistics about the current data set.
	[clear_tables.cgi]: When a user submits the appropriate html form, this script will be
		called and clear all gene and annotation information from the database, allowing for a
		new file to be uploaded.
	[Gene_Query.cgi]: When searching by genes, the user will submit a form for the gene query.
		The gene code to be searched will be sent to this script, which runs a sql query and returns
		appropriate information.
	[GO_Query.cgi]: This script runs after the annotation search form is submitted.
		The script generates the appropriate sql based off of the user's entry and returns
		the results formatted into an html table.
>>> Data Storage <<<
Data for this system is stored in four separate tables. These tables represent the genes,
gene annotations, and go terms.
	[create_tables.sql]: This is sql code that must be run from within a mysql shell,
		but will create the needed tables for the user.
>>> Core Ontology Download <<<
Each night, the server runs a cronjob to install the most recent Core Ontology file (go.obo)
This is accomplished by a cronjob which runs a bash script, which in turn runs a perl script:
	[update_go.sh]: This script will remove the current go.obo file, download the newest one,
		and then run read_in_go.pl using this file.
	[read_in_go.pl]: This script will parse a Core Ontology file and store information
		about each term into our database.
		NOTE: In order for this script to work, the tables must already exist in the database.
	[go.log]: This file contains the output from the read_in_go.pl script, which simply
		outputs the date and time of the last upload.

============[SETUP]==============
[1] File placement:
To set up the files for this system so that it runs out of your own directory,
follow the subsequent steps
	1. Place following files into the same location in the public_html directory:
		> HomePage.html
		> read_in_terms.cgi
		> clear_tables.cgi
		> Gene_Query.cgi
		> GO_Query.cgi
		> read_in_go.pl
		> update_go.sh
	2. Use 'chmod 755 <file_name>' to set executable permissions for the following files:
		> clear_tables.cgi
		> Gene_Query.cgi
		> GO_Query.cgi
		> read_in_terms.cgi
		> update_go.sh
[2] Database initialization:
In order to set up the database for this system correctly, you must have a 
database set up to store the tables and records for this project. Once you have a
database, the following must be done:
	1. Rename database credentials in the appropriate files
		In each of the following files, navigate to the "getDBH" subroutine.
		Here, credentials for connection to your database are to be specified.
		Replace what I've written with your information.
			> GO_Query.cgi
			> Gene_Query.cgi
			> clear_tables.cgi
			> read_in_terms.cgi
			> read_in_go.pl
	2. Run create_tables.sql.
		Open a mysql console using the following commands:
			'mysql -u <your_uname> -p'
		You will be prompted for a password, then taken into the mysql console.
		Run:
			'use <your_database_name>;'
			'source <path_to_file>/create_tables.sql;'
		You should see some feedback telling you that queries have been run.
		Your tables are now set up properly.
	3. Run update_go.sh.
		The first time that you set up your database, you'll need to run the update_go script.
		This can be done manually by simply calling './update_go.sh' from the terminal.
		NOTE: The file must be set as an executable as shown above
		This will download the go.obo file into the public_html directory and populate the database.
[3] Crontab setup:
To get the update running each night, use the following command to create a job
that will run every night at midnight:
	'crontab -e'
	This will take you into the text editor of your choice. Type the following at the end of the file:
	'0 0 * * * ./update_go.sh > ~/cron.out'
It is likely that you'll need to get your account approved by the system administrator
in order to run jobs using cron.

=========[MAINTENANCE]==========
[1] Checking the crontab
One day after you submit the cronjob (the command written in the crontab),
check the go.log. If the update has run overnight, then the crontab is set up successfully.
