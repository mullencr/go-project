CREATE TABLE genes (
	id			INT			AUTO_INCREMENT	PRIMARY KEY,
	gene_name	varchar(60)	NOT NULL,
);

CREATE TABLE go_annotations (
	id				INT	AUTO_INCREMENT	PRIMARY KEY,
	go_id 			INT REFERENCES go_terms(go_id),
	p_value			varchar(255),
	corr_p_value	varchar(255),
	set_frequency	INT,
	set_total		INT,
	ref_frequency	INT,
	ref_total		INT,
	description		varchar(900)
);

CREATE TABLE gene_annotation_join (
	annotation_id	INT	REFERENCES	go_annotations(id),
	gene_id			INT	REFERENCES	genes(id),
	PRIMARY KEY (annotation_id, gene_id)
);

/*
CREATE TABLE go_terms (
	go_id			INT	PRIMARY KEY,
	category		VARCHAR(60),
	description		VARCHAR(900)
);
*/
