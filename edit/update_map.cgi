#!/opt/perl5/perls/perl-5.14.0/bin/perl
use CGI;
use DBI;
use POSIX 'strftime';
use strict;
our( $dbh, $room );
my $q = CGI->new;
my $level = $q->param('level');
my $x = $q->param('x');
my $y = $q->param('y');
$dbh = DBI->connect('dbi:mysql:database=javatar','avatar','WRENtlal');
my $sth = $dbh->prepare(<<EOSQL);
SELECT MAX(version) FROM levels WHERE num=?
EOSQL
$sth->execute( $level );
my( $version ) = $sth->fetchrow_array;



$sth = $dbh->prepare(<<EOSQL);
SELECT * FROM map WHERE x=? AND y=? AND level=? AND end='9999-12-31 23:59:59'
EOSQL
$sth->execute( $x, $y, $level );
my $room = $sth->fetchrow_hashref;

$sth = $dbh->prepare(<<EOSQL);
SELECT * FROM map WHERE x=? AND y=? AND level=? AND end=?
EOSQL
$sth->execute( $x, $y, $level, $$room{'start'} );
my $orig = $sth->fetchrow_hashref;


my $to_check = { %{$room || {}} };
delete $$to_check{$_} for qw( id x y level version start end tpmeta );

my %checkboxes = ( dark=>1, nomagic=>1, illusion=>1, exting=>1, traps=>1 );

my $changed = 0;
my $orig_changed = 0;
my %changed;
foreach (keys %$to_check) {
    my $val = $q->param($_);
    $val = undef if $val eq '';
    if ( ! defined $val and $checkboxes{$_} ) {
        $val = 0;
    }
    if ( $val ne $$to_check{$_} ) {
        $changed ++;
        $changed{$_} = $val;
    }
    if ( $val ne $$orig{$_} ) {
        $orig_changed ++;
#        warn "$_: new $val differs from old $$orig{$_}\n";
    }
}

if ( $changed == 0 ) {
    print $q->redirect("http://javatar.mikomi.org/edit/?level=$level&x=$x&y=$y");
    exit(0);
}

if ( $$room{'version'} ) {
    my $date = strftime("%Y-%m-%d %H:%M:%S", localtime());
    # Update the existing record to have an end date
    $dbh->do('UPDATE map SET end=? WHERE id=?',undef,$date,$$room{'id'});
    # Insert a new record
    my $fields = join ',', $q->param;
    my $ph     = join ',', map { '?' } $q->param;
    my @values = map { ($q->param($_) eq '')?undef:$q->param($_) } $q->param;
    $dbh->do("INSERT INTO map ( $fields, start ) VALUES ($ph, ?)",undef,
        @values, $date);
} else {
    if ( $orig_changed ) {
        my $fields = join ',', map { "$_=?" } keys %changed;
    #     Update the existing record with our changes.
        $dbh->do("UPDATE map SET $fields WHERE id=?",undef,values %changed,$$room{'id'});
    } else {
    #     Delete the existing record and set the end date to be 9999.
        $dbh->do('DELETE FROM map WHERE id=?',undef,$$room{'id'});
        $dbh->do("UPDATE map SET end='9999-12-31 23:59:59' WHERE id=?",undef,$$orig{'id'});
    }
}

print $q->redirect("http://javatar.mikomi.org/edit/?level=$level&x=$x&y=$y");
exit(0);
