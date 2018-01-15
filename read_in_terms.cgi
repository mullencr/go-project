#!/usr/bin/perl -w
use strict;
use DBI;
use CGI;
use File::Basename;
# This is for error reporting to the browser
use CGI::Carp qw(fatalsToBrowser);

# Set max file size
$CGI::POST_MAX = 1024 * 5000;

# Define what characters are safe to use in the filename.
# allowing chars like / could let someone upload to any dir they wanted
my $safe_filename_characters = "a-zA-Z0-9_.-";

# Define the upload directory
my $upload_dir = "/home/mullencr/public_html/upload";

my $query = new CGI;
print $query->header();

my $filename = $query->param("myfile1");
# If there is a problem, $filename will be empty
if ( !$filename ) {
	print $query->header();
	print "There was a problem uploading your annotation (try a smaller file).";
	exit;
}

# This goes to a temporary file created by CGI.pm
my $upload_filehandle = $query->upload("myfile1");

my $dbh = getDBH();
my $state = 0;
while(my $line = <$upload_filehandle>) {
	chomp($line);
	# parse the file appropriately.
	if (substr($line, 0, 12) eq "The selected") {
		# First look for the genes that will be in it.
		$state = 1;
	} elsif (substr($line, 0, 14) eq "No annotations") {
		# Next see if we're on to state 2 (don't read anything during this state)
		$state = 2;
	} elsif (substr($line, 0, 5) eq "GO-ID") {
		# Next see if we're on to state 3 (the gene annotation part)
		$state = 3;
	} elsif ($state == 1) {
		# Read those genes in and add them all to the database.
		# The else is so we don't read "The" and "selected" in as genes
		# Check to make sure the line isn't blank
		if($line ne '') {
			# Split the line
			my @genes = split(/\t/, $line);
			# For each item in the split array, call the add gene db function.
			foreach my $gene (@genes) {
				create_gene($dbh, $gene);
			}
		}
	} elsif ($state == 3) {
		# Make a record for the annotation using the first few columns.
		my @an = split(/\t/, $line);
		create_annotation($dbh, $an[0], $an[1], $an[2], $an[3], $an[4], $an[5], $an[6], $an[7]);
		# Split the last column by |. Then select to grab this record's ID. (ugh)
		my $an_id = get_an_id($dbh, $an[0]);
		my @genes = split(/\|/, $an[8]);
		# For each element in the last column, add a record to the join table
		foreach my $gene (@genes) {	
			my $gene_id = get_gene_id($dbh, $gene);
			create_ga_join($dbh, $an_id, $gene_id);
		}
	}
}
write_index();
write_set_info($dbh);

# ============ Subroutines ==============
sub getDBH {
	# setup database connection variables
	my $user = "mullencr";
	my $password = "bio466";
	my $host = "localhost";
	my $driver = "mysql";	
	# connect to database
	my $dsn = "DBI:$driver:database=mullencr;host=$host";
	my $dbh = DBI->connect($dsn, $user, $password);
	return $dbh;
}

sub create_gene {
	my $dbh = shift;
	my $gene_name = shift;	
	my $sql = "insert into mullencr.genes (gene_name) values ('$gene_name');";
	my $query_handle = $dbh->prepare($sql);
	$query_handle->execute();
}

sub create_annotation {
	my $dbh = shift;
	my $go_id = shift;
	my $p_val = shift;
	my $cp_val = shift;
	my $set_freq = shift;
	my $set_tot = shift;
	my $ref_freq = shift;
	my $ref_tot = shift;
	my $desc = shift;
	my $sql = "insert into mullencr.go_annotations (go_id, p_value, corr_p_value, set_frequency, ref_frequency, set_total, ref_total, description) values ($go_id, $p_val, $cp_val, $set_freq, $set_tot, $ref_freq, $ref_tot, '$desc');";
	my $query_handle = $dbh->prepare($sql);
	$query_handle->execute();
}

sub create_ga_join {
	my $dbh = shift;
	my $an_id = shift;
	my $gene_id = shift;
	my $sql = "insert into mullencr.gene_annotation_join (annotation_id, gene_id) values ($an_id, $gene_id);";
	my $query_handle = $dbh->prepare($sql);
	$query_handle->execute();
}

sub get_an_id {
	my $dbh = shift;
	my $go_id = shift;
	my $sql = "SELECT id FROM mullencr.go_annotations WHERE go_id = $go_id;";	
	my $rowsref = $dbh->selectall_arrayref($sql) || die $dbh->errstr;
	my @rows = @{$rowsref};	
	my @row = @{$rows[0]};
	return $row[0];
}

sub get_gene_id {
	my $dbh = shift;
	my $gene_name = shift;
	my $sql = "SELECT id FROM mullencr.genes WHERE gene_name LIKE '$gene_name';";
	my $rowsref = $dbh->selectall_arrayref($sql) || die $dbh->errstr;
	my @rows = @{$rowsref};
	my @row = @{$rows[0]};
	return $row[0];
}

sub write_index {
	open(FIN, "HomePage.html");
	while(my $line = <FIN>) {
		print $line;
	}
}

sub write_set_info {
	my $dbh = shift;
	my $sql = "SELECT COUNT(*) FROM mullencr.go_annotations;";
	my $rowsref = $dbh->selectall_arrayref($sql) || die $dbh->errstr;
	my @rows = @{$rowsref};
	my @row = @{$rows[0]};
	print "<br/><h3>Current Set Information</h3>";
	print "<p>Number of annotations in set: $row[0]</p>";
	my $update_status = `tail go.log`;
	print "<p>$update_status</p>";
	my $sql = "SELECT tr.category, count(*) AS sum, ((count(*)/(SELECT COUNT(*) FROM go_annotations))*100) AS percentage FROM go_annotations AS an JOIN go_terms AS tr ON an.go_id = tr.go_id GROUP BY tr.category ORDER BY sum;";
	my $rowsref = $dbh->selectall_arrayref($sql) || die $dbh->errstr;
	my @rows = @{$rowsref};
	print "<table border=1 cellspacing=0 cellpadding=3><tr><th>Sub Ontology</th><th>Number of Annotations</th><th>Percent of Total (%)</tr>";
        for (my $i = 0; $i < $#rows + 1; $i++) {
        	my @row = @{$rows[$i]};
                print "<tr>";
                for (my $c = 0; $c < $#row+1; $c++) {
                	my $out = $row[$c];
			$out =~ s/biological_process/Biological Process/g;
			$out =~ s/molecular_function/Molecular Function/g;
			$out =~ s/cellular_component/Cellular Component/g;
			print "<td>$row[$c]</td>"
                }
                print "</tr>";
        }
        print "</table><br/>";	
}
