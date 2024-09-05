#!/opt/perl5/perls/perl-5.14.0/bin/perl
use strict;
use DBI;
use CGI;

my $q = CGI->new;
my $dbh = DBI->connect('dbi:mysql:database=javatar','avatar','WRENtlal');

my $level = $q->param('level') || 1;
my $x = $q->param('x');
my $y = $q->param('y');

my $sth = $dbh->prepare(<<EOSQL);
SELECT MAX(version) FROM levels WHERE num=?
EOSQL
$sth->execute( $level );
my( $version ) = $sth->fetchrow_array;

$sth = $dbh->prepare(<<EOSQL);
SELECT COUNT(*) FROM map WHERE level=? AND version IS NULL
EOSQL
$sth->execute( $level );
my( $changed_rooms ) = $sth->fetchrow_array;

if ( $changed_rooms ) {
    $version ++;
    $dbh->do("INSERT INTO levels ( num, version, created, whom ) VALUES ( ?, ?, NOW(), ? )",
        undef, $level, $version, $ENV{'REMOTE_USER'} );
    $dbh->do("UPDATE map SET version=? WHERE level=? AND version IS NULL", undef,$version,$level);
    chdir("/var/www/javatar/render");
    my $paddedlevel = $level;
    if (length(sprintf "%d", $level) < 2) {
        $paddedlevel = '0'.$level;
    }
    my $fname = "map_$paddedlevel";
    my $scratch = "/var/www/javatar/scratch";
    system("/opt/perl5/perls/perl-5.14.0/bin/perl","draw_map2.pl",$level,$version,"$scratch/${fname}_v$version.svg");
    system("convert","$scratch/${fname}_v$version.svg","-depth", "8", "-colors", "256", "$scratch/${fname}_v$version.png");
#    system("rsvg","$scratch/${fname}_v$version.svg","$scratch/${fname}_v$version.png");
    system("mv","$scratch/${fname}_v$version.png","/var/www/javatar/maps/${fname}_v$version.png");
}

print $q->redirect("http://javatar.mikomi.org/?level=$level&x=$x&y=$y");
