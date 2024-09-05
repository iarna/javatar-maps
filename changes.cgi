#!/opt/perl5/perls/perl-5.14.0/bin/perl
use CGI;
use DBI;
use strict;

my $q = CGI->new();

print $q->header();
my $dbh = DBI->connect('dbi:mysql:database=javatar','avatar','WRENtlal');


print <<EOHTML;
<html>
<head>
<title>Javatar: Mapping Changes</title>
<style>
\@media print {
    #navigation { display: none; }
}
</style>
</head>
<body>
<div id="navigation">
<a href="about.html">About</a> &nbsp; &nbsp; <a href="changes.cgi">Changes</a> &nbsp; &nbsp; <a href="edit.html">Editing</a><br>
<a href="legend.html">Legend</a>
EOHTML
my $levels = $dbh->prepare(<<EOSQL);
SELECT DISTINCT num
FROM levels
ORDER BY CAST(num AS SIGNED), num
EOSQL
$levels->execute();
while ( my $level = $levels->fetchrow_hashref ) {
  print qq{ &nbsp; &nbsp; <a href="/?level=}.$level->{num}.qq{">}.$level->{num}.qq{</a>};
}
print <<EOHTML;
</div>
Javatar - Mapping Changes<br>
<br>
<p>These maps started life as an exact copy of the maps at 
<a href="http://www.heavyharmonies.com/Avatar/maps.html">Heavy Harmonies</a>.
<ul>
EOHTML
my %checkboxes = ( dark=>1, nomagic=>1, illusion=>1, exting=>1, traps=>1 );
my $rooms = $dbh->prepare(<<EOSQL);
SELECT * FROM map WHERE level=? AND version=? ORDER BY start DESC
EOSQL
my $old = $dbh->prepare(<<EOSQL);
SELECT * FROM map WHERE level=? AND x=? AND y=? AND end=?
EOSQL
my $revisions = $dbh->prepare(<<EOSQL);
SELECT num as level, version, created, whom
FROM levels
WHERE version > 1
ORDER BY created DESC
LIMIT 150
EOSQL
$revisions->execute();
my $date;
while ( my $rev = $revisions->fetchrow_hashref ) {
    my $this_date = substr( $$rev{'created'}, 0,10 );
    if ( $date ne $this_date ) {
        print "<b>$this_date</b>\n";
        $date = $this_date;
    }
    print "<li>Revision #$$rev{'version'} of Level $$rev{'level'} created by $$rev{'whom'}\n";
    $rooms->execute( $$rev{'level'}, $$rev{'version'} );
    my %changes;
    while ( my $room = $rooms->fetchrow_hashref ) {
        $old->execute( $$room{'level'}, $$room{'x'}, $$room{'y'}, $$room{'start'} );
        my $old_room = $old->fetchrow_hashref;
        foreach (keys %$room ) {
            next if $_ =~ /^(?:id|x|y|level|version|start|end|tpmeta)$/;
            if ( $$room{$_} ne $$old_room{$_} ) {
                if ( $checkboxes{$_} ) {
                    if ( $$room{$_} ) {
                        push @{ $changes{"Set $_"} }, $room;
                    } else {
                        push @{ $changes{"Cleared $_"} }, $room;
                    }
                } else {
                    push @{ $changes{"Changed $_ from $$old_room{$_} to $$room{$_}"} }, $room;
                }
            }
        }
    }
    print "<ul>\n";
    foreach ( sort keys %changes ) {
        print "<li>$_ at ";
        my $out = join(', ', map { qq[<a href="/?level=$$_{'level'}&x=$$_{'x'}&y=$$_{'y'}">$$_{'x'},$$_{'y'}</a>] } @{ $changes{$_} } );
        $out =~ s{(.*>),}{$1 and};
        print $out;
        print ".</li>\n";
    }
    print "</ul>\n";
    print "</li>\n";
}
print "</ul>";
print <<EOHTML
</body>
</html>
EOHTML
