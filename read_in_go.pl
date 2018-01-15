#! /usr/bin/perl
use strict;
# import proper Perl modules and Classes
use strict;
use DBI;

my $file = shift;
open(FIN, $file);
my $dbh = getDBH();
clearGo($dbh);
my $reading = 0;
my ($go_id, $desc, $namespace) = ('', '', '');
# Read through the file and find the significant lines.
while(my $line = <FIN>) {
	chomp($line);
	if ( substr($line, 0, 1) eq '[' ) {	
		# We've reached a new section. Write out what we have
		if ($go_id ne '' && $namespace ne '' && $desc ne '') {
			# do the insertion.	
			insertOntology($dbh, $go_id, $namespace, $desc);
		}
		if ($line eq '[Term]') {	
			# Set reading to true.
			$reading = 1;
		} else {
			# Prevents us from reading in the [Typedef] information
			# However, we still want to write the last record when we hit a [Typedef]
			# Which is why we don't write the last one after the loop finishes.
			$reading = 0;
		}
		# Set the values to read in equal to blank.
		($go_id, $desc, $namespace) = ('', '', '');
	} elsif ($reading == 1 && substr($line, 0, 3) eq "id:") {
		# record the id. WIll look like: 'id: GO:0000002'	
		$go_id = substr($line, 8);	
	} elsif ($reading == 1 && substr($line, 0, 5) eq 'name:') {
		# record the description.
		$desc = substr($line, 6);
		$desc =~ s/'//g;
	} elsif ($reading == 1 && substr($line, 0, 10) eq 'namespace:') {
		# read in the category.
		$namespace = substr($line, 11);
	}
}
my $datestring = localtime();
printf("Core Ontology last updated: $datestring\n");

# =========================== [ subroutines ] =====================
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

sub insertOntology {
	my $dbh = shift;
	my $go_id = shift;
	my $category = shift;
	my $desc = shift;
	# Insert the info	
	my $sql = "insert into mullencr.go_terms (go_id, category, description) values ($go_id, '$category', '$desc');";
	my $query_handle = $dbh->prepare($sql);
	$query_handle->execute();
}

sub clearGo {
	my $dbh = shift;
	my $sql = "select * from mullencr.go_terms;";
	my $rowsref = $dbh->selectall_arrayref($sql) || die $dbh->errstr;
	my @rows = @{$rowsref};
	if ($#rows+1 > 0) {
		$sql = "truncate table mullencr.go_terms;";
		my $query_handle = $dbh->prepare($sql);
		$query_handle->execute();
	}
}
