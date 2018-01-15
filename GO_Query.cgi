#!/usr/bin/perl -w
use strict;
use CGI;
use DBI;
my $GO_Query=new CGI;
my $dbh = getDBH();
use CGI::Carp qw(fatalsToBrowser);
  
print $GO_Query->header();
print $GO_Query->start_html(-title=>'Form Results',
                       -author=>'LG CM');

my $GO_ID = $GO_Query->param("GO_ID");
if (!$GO_ID) {
	$GO_ID = "";
}
my $Sub_ontology = $GO_Query->param("sub-ontology");
if (!$Sub_ontology) {
	$Sub_ontology = "";
}
my $GO_Term=$GO_Query->param("GO_Term");
if (!$GO_Term) {
	$GO_Term = "";
}

write_index();
write_set_info($dbh);
GO_Query1($dbh, $GO_ID, $Sub_ontology, $GO_Term);

print $GO_Query->end_html."\n";

# ============================== Subroutines ==============================
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

sub GO_Query1 {
	my $dbh = shift;
	my $GO_ID = shift;
	my $Sub_ontology = shift;
	my $GO_Term = shift;
	my $sql = "SELECT an.go_id, tr.category, an.p_value, an.corr_p_value, an.set_frequency, an.set_total, an.ref_frequency, an.ref_total, an.description FROM go_annotations AS an JOIN go_terms AS tr ON an.go_id = tr.go_id WHERE ";
	my @conditions = ();
	if ($GO_ID ne "") {
		push(@conditions, "an.go_id = $GO_ID");
	}
	if ($Sub_ontology ne "") {
		if ($Sub_ontology eq "BP") {
			push(@conditions, "tr.category LIKE 'biological_process'");
		} elsif ($Sub_ontology eq "CC") {
			push(@conditions, "tr.category LIKE 'cellular_component'");
		} elsif ($Sub_ontology eq "MF") {
			push(@conditions, "tr.category LIKE 'molecular_function'");
		}
	}
	my $cons = " 1=0;";
	if ($GO_Term ne "") {
		push(@conditions, "an.description LIKE '%$GO_Term%'");
	}
	if($#conditions+1 > 0) {
		$cons = (join(" AND ", @conditions));
	}
	$sql = $sql.$cons." ORDER BY an.go_id;";
	my $rowsref = $dbh->selectall_arrayref($sql) || die $dbh->errstr;
	my @rows = @{$rowsref};
	print "<h4>Annotations</h4>";
	print "<table border=1 cellspacing=0 cellpadding=3><tr><th>go_id</th><th>Sub Ontology</th><th>p_value</th><th>corr_p_value</th><th>set_frequency</th><th>set_total</th><th>ref_frequency</th><th>ref_total</th><th>enrichment</th><th>description</th></tr>";
	if ($#rows+1 > 0) {	
		foreach my $row_ref (@rows) {
			my @row = @{$row_ref};
			print "<tr>";
			for(my $i = 0; $i < $#row+1; $i++) {
				if ($i == 8) {
					# Calculate the enrichment.
					if (($row[4]/$row[5]) > ($row[6]/$row[7])) {
						print "<td>Up-Regulated in test set</td>";
					} else {
						print "<td>Not Up-Regulated in test set</td>";
					}
				}
				print "<td>$row[$i]</td>";
			}
			print "</tr>";
		}
		print "</table>";
	}
	$sql = "SELECT DISTINCT ge.gene_name FROM genes AS ge JOIN gene_annotation_join AS jo ON ge.id = jo.gene_id JOIN go_annotations AS an ON jo.annotation_id = an.id WHERE an.id IN (SELECT an.id FROM go_annotations AS an JOIN go_terms AS tr ON an.go_id = tr.go_id WHERE $cons)";	
	my $rowsref = $dbh->selectall_arrayref($sql) || die $dbh->errstr;	
	my @rows = @{$rowsref};
	print "<h4>Genes from current selection</h4>";
	print "<table border=1 cellspacing=0 cellpadding=3>";
	print "<tr>";
	for(my $i = 0; $i < $#rows+1; $i++) {
		my @row = @{$rows[$i]};
		if ($i%6 == 0) {
			print "</tr><tr>";
		}
		print "<td>$row[0]</td>";
	}
	print "</tr>";
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

