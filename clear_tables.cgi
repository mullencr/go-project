#!/usr/bin/perl -w
use strict;
use CGI;
use DBI;
use CGI::Carp qw(fatalsToBrowser);

my $dbh = getDBH();
my $cgi = new CGI;
print $cgi->header();

clearDB($dbh);
write_index();
write_set_info($dbh);

#===================== Subroutines ===================
sub clearDB {
	my $dbh = shift;
	my $sql = "truncate table gene_annotation_join;";
	my $query_handle = $dbh->prepare($sql);
	$query_handle->execute();
	$sql = "truncate table genes;";
	$query_handle = $dbh->prepare($sql);
	$query_handle->execute();
	$sql = "truncate table go_annotations;";
	$query_handle = $dbh->prepare($sql);
	$query_handle->execute();
}

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
        print "</table></br>";
}

