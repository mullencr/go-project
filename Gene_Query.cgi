#!/usr/bin/perl -w
use strict;
use CGI;
use DBI;
my $Gene_Query=new CGI;   ## CGI->new();
my $dbh = getDBH();
use CGI::Carp qw(fatalsToBrowser);

  
print $Gene_Query->header();
print $Gene_Query->start_html(-title=>'Form Results',
                       -author=>'LG CM');
                       
my $Gene = $Gene_Query->param("Gene");
if (!$Gene){
	$Gene = "";
}

write_index();
write_set_info($dbh);
Gene_Query1($dbh, $Gene);

print $Gene_Query->end_html."\n";  


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

sub Gene_Query1 {
	my $dbh = shift;
	my $Gene = shift;	
	my $sql = "SELECT * FROM genes WHERE gene_name LIKE '$Gene';";
	my $rowsref = $dbh->selectall_arrayref($sql) || die $dbh->errstr;
	my @rows = @{$rowsref};		
	if ($#rows+1 > 0) {
		my $sql = "SELECT an.go_id, tr.category, an.p_value, an.corr_p_value, an.set_frequency, an.set_total, an.ref_frequency, an.ref_total, an.description FROM genes AS ge JOIN gene_annotation_join AS jo ON ge.id= jo.gene_id JOIN go_annotations AS an ON an.id = jo.annotation_id JOIN go_terms AS tr ON tr.go_id = an.go_id WHERE ge.gene_name like '$Gene' ORDER BY an.go_id;";
		my $rowsref = $dbh->selectall_arrayref($sql) || die $dbh->errstr;
		my @rows = @{$rowsref};
		if ($#rows+1 > 0) {
			print "<table border=1 cellspacing=0 cellpadding=3><tr><th>go_id</th><th>Sub Ontology</th><th>p_value</th><th>corr_p_value</th><th>set_frequency</th><th>set_total</th><th>ref_frequency</th><th>ref_total</th><th>enrichment</th><th>description</th></tr>";
			for (my $i = 0; $i < $#rows + 1; $i++) {
				my @row = @{$rows[$i]};
				print "<tr>";
				for (my $c = 0; $c < $#row+1; $c++) {
					if ($c == 8) {
                                        	# Calculate the enrichment.
                                        	if (($row[4]/$row[5]) > ($row[6]/$row[7])) {
                                                	print "<td>Up-Regulated in test set</td>";
                                        	} else {
                                                	print "<td>Not Up-Regulated in test set</td>";
                                        	}
                                	}
					print "<td>$row[$c]</td>"
				}
				print "</tr>";
			}
			print "</table>";
		} else {
			print "<p>Selected gene does have significant expression</p><br/><p>Selected gene does not have any significant annotations.</p>";
		}	
	} else {
		print "<p>Selected gene does not have significant expression</p>";
	}	
}

sub write_index {   ## what does this subroutine do?
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

