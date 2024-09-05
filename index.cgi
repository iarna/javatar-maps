#!/opt/perl5/perls/perl-5.14.0/bin/perl
use CGI;
use DBI;
use strict;
our $dbh;
$dbh = DBI->connect('dbi:mysql:database=javatar','avatar','WRENtlal');

our( $level, $x, $y, $version, $tp_locations, $teleporters, $legend,
     $movement, $map, $mapembed, $levels );

main();
exit(0);


sub cat($) {
    open(my $file, $_[0] )
        or die "Couldn't open $_[0]: $!\n";
    return join '', <$file>;
}

sub main { 
    my $q = CGI->new;
    $level = $q->param('level') || '1';
    $x = $q->param('x') || 0;
    $y = $q->param('y') || 0;
    $levels = '';
    for my $lv (get_levels()) {
        $levels .= qq{<a href="/?level=$lv">$lv</a>};
    }
    $version = get_version( scalar $q->param('version') );
    get_teleporters( $dbh, $level, $version );
    my $paddedlevel = $level;
    if (length(sprintf "%d", $level) < 2) {
        $paddedlevel = '0'.$level;
    }
    $map = sprintf "maps/map_%s_v%d.png", $paddedlevel, $version;
    get_legend( get_room() );
    my $template = cat "index_template.html";
    var_replace( \$template );
    print $q->header("text/html; charset=utf-8");
    print $template;
}

sub var_replace {
    my( $tmpl ) = @_;
    no strict 'refs';
    $$tmpl =~ s{\$(\w+)}{${$1}}ge;
}

sub get_version {
    my( $version ) = @_;
    if ( ! $version ) {
        my $sth = $dbh->prepare(<<EOSQL);
SELECT MAX(version) FROM levels WHERE num=?
EOSQL
        $sth->execute( $level );
        ( $version ) = $sth->fetchrow_array;
    }
    return $version;
}

sub get_levels {
    my $levels = $dbh->prepare(<<EOSQL);
SELECT DISTINCT num
FROM levels
ORDER BY CAST(num AS SIGNED), num
EOSQL
    $levels->execute();
    my @levellist;
    while ( my $level = $levels->fetchrow_hashref ) {
        push @levellist, $level->{num};
    }
    return @levellist;

}

sub get_room {
    if ( $x and $y ) {
        my $sth = $dbh->prepare(<<EOSQL);
SELECT created FROM levels where num=? AND version=?
EOSQL
        $sth->execute( $level, $version );
        my( $created ) = $sth->fetchrow_array;
        $sth = $dbh->prepare(<<EOSQL);
SELECT * FROM map WHERE x=? AND y=? AND level=? AND (
    version=? OR
        ( version IS NOT NULL AND start < ? AND end > ? ) )
EOSQL
        $sth->execute( $x, $y, $level, $version, $created, $created );
        return $sth->fetchrow_hashref;
    }
}

sub get_legend { 
    my( $room ) = @_;
    if ( ! $x or ! $y ) {
        $legend = cat 'index_legend.html';
    } else {
        $legend = cat 'index_nolegend.html';
        $movement = '';
        if ( $$room{'env'} =~ /^chute(\d)/ ) {
            my $target_level =$level +  $1;
           $movement = <<EOHTML
<hr>
<a href="?x=$x&y=$y&level=$target_level">Follow chute</a>
EOHTML
        }
        if ( $$room{'movement'} eq 'stairsup' ) {
            my $target_level =$level - 1;
           $movement = <<EOHTML
<hr>
<a href="?x=$x&y=$y&level=$target_level">Take stairs</a>
EOHTML
        } elsif ( $$room{'movement'} eq 'stairsdown' ) {
            my $target_level =$level + 1;
           $movement = <<EOHTML
<hr>
<a href="?x=$x&y=$y&level=$target_level">Take stairs</a>
EOHTML
        } elsif ( $$room{'movement'} eq 'transup' ) {
            my $target_level =$level - 1;
           $movement = <<EOHTML
<hr>
<a href="?x=$x&y=$y&level=$target_level">Follow transporter</a>
EOHTML
        } elsif ( $$room{'movement'} eq 'transdown' ) {
            my $target_level =$level + 1;
           $movement = <<EOHTML
<hr>
<a href="?x=$x&y=$y&level=$target_level">Follow transporter</a>
EOHTML
        } elsif ( $$room{'movement'} eq 'tp' ) {
            my $act = '';
            my $onmouseover = '';
            my $onmouseout = '';
            if ( $$room{'tz'} eq $level ) {
                $onmouseover .= 
                    qq/avatar.showSources([{'x':$$room{'tx'},'y':$$room{'ty'}}]);/;
                $onmouseout .= qq/avatar.showSources([]);/;
            }
            $onmouseover .= qq/highlightTP($$room{'tx'},$$room{'ty'},$$room{'tz'});/;
            $onmouseout  .= qq/unhighlightTP($$room{'tx'},$$room{'ty'},$$room{'tz'});/;
            if ( $onmouseover ) {
                $act .= qq{ onMouseOver="$onmouseover"};
            }
            if ( $onmouseout ) {
                $act .= qq{ onMouseOut="$onmouseout"};
            }
            $movement = <<EOHTML
<hr>
<a $act href="?x=$$room{'tx'}&y=$$room{'ty'}&level=$$room{'tz'}">Follow teleporter</a>
EOHTML
        }
        var_replace( \$legend );
    }
}

sub get_teleporters {
    my( $dbh, $level, $version ) = @_;
    my $sth = $dbh->prepare(<<EOSQL);
SELECT created FROM levels where num=? AND version=?
EOSQL
    $sth->execute( $level, $version );
    my( $created ) = $sth->fetchrow_array;
    $sth = $dbh->prepare(<<EOSQL);
SELECT *
FROM map
WHERE 
    level=? AND movement='tp' AND 
    ( version=? OR ( 
      ( version IS NOT NULL AND start < ? AND end > ? ) ) )
ORDER BY y,x
EOSQL
    $sth->execute( $level, $version, $created, $created );
    my( %tp, @tp );

    while ( my $room = $sth->fetchrow_hashref ) {
        my $hash = "$$room{'tx'},$$room{'ty'},$$room{'tz'}";
        unless ( $tp{$hash} ) {
            push @tp, $room;
        }
        push( @{ $tp{$hash} }, $room);
        $room->{tx} ||= 0;
        $room->{ty} ||= 0;
        $room->{tz} ||= 0;
        $tp_locations .= <<EOHTML;
tp_locations['/$$room{x},$$room{y}'] = { 'x':$$room{tx}, 'y':$$room{'ty'}, 'z':$$room{'tz'} };
EOHTML
    }
    my $internal = <<EOHTML;
<table cellspacing="0" cellpadding="0" border="0">
EOHTML
    $teleporters = $internal;
    for ( my $num = 0; $num < @tp; $num ++ ) {
        my $target;
        if ( $tp[$num]{'tz'} ne $level or !$version) {
            $target = "opentp($tp[$num]{'tx'},$tp[$num]{'ty'},$tp[$num]{'tz'})";
        } else {
            $target = "opentpv($tp[$num]{'tx'},$tp[$num]{'ty'},$tp[$num]{'tz'},$version)";
        }
        my $hash = "$tp[$num]{'tx'},$tp[$num]{'ty'},$tp[$num]{'tz'}";
        my $source = join ', ', map { "{'x':$$_{'x'},'y':$$_{'y'},'z':$$_{'level'}}" } @{$tp{$hash}};
        $teleporters .= sprintf
            qq!<tr id="tp$tp[$num]{'tx'}_$tp[$num]{'ty'}_$tp[$num]{'tz'}"><td class="src" onmouseover="avatar.showSources([$source]);">%d:</td>!,$num+1;
        $teleporters .= sprintf 
            qq{<td valign="bottom">&nbsp;<span class="targ" onmouseover="avatar.showSources([$source]);" onclick="$target">→</span></td>}.
            qq{<td valign="bottom" class="targ" onmouseover="avatar.showSources([$source]);" onclick="$target">%d,</td>}.
            qq{<td valign="bottom" class="targ" onmouseover="avatar.showSources([$source]);" onclick="$target">%d</td>},
            $tp[$num]{'tx'},$tp[$num]{'ty'};
        if ( $tp[$num]{'tz'} ne $level ) {
            $teleporters .= sprintf qq{<td valign="bottom" class="targ" onmouseover="avatar.showSources([$source]);" onclick="$target">,%2d</td>}, $tp[$num]{'tz'};
        }
        $teleporters .= "</tr>\n";
        if ( $num % 2 and $num < 2 ) {
            $teleporters .= qq{</table></td><td style="width: 7em;" valign="top">$internal};
        }
    }
    $teleporters .= qq{</table>};
}
