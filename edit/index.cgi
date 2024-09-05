#!/opt/perl5/perls/perl-5.14.0/bin/perl
use CGI;
use DBI;
use strict;
our( $dbh, $room );
my $q = CGI->new;
my $level = $q->param('level') || '1';
my $x = $q->param('x');
my $y = $q->param('y');
my $version = $q->param('version');

$dbh = DBI->connect('dbi:mysql:database=javatar','avatar','WRENtlal');

if ( ! $version ) {
    my $sth = $dbh->prepare(<<EOSQL);
SELECT MAX(version) FROM levels WHERE num=?
EOSQL
    $sth->execute( $level );
    ( $version ) = $sth->fetchrow_array;
}

my $sth = $dbh->prepare(<<EOSQL);
SELECT COUNT(*) FROM map WHERE level=? AND version IS NULL
EOSQL
$sth->execute( $level );
my( $changed_rooms ) = $sth->fetchrow_array;

my $sth = $dbh->prepare(<<EOSQL);
SELECT * FROM map WHERE x=? AND y=? AND level=? AND end='9999-12-31 23:59:59'
EOSQL
$sth->execute( $x, $y, $level );
$room = $sth->fetchrow_hashref;

print $q->header("text/html; charset=utf-8");
print <<EOHTML;
<html>
<head>
<title>Javatar: Level $level</title>
<style>
\@media print {
    #navigation { display: none; }
}
</style>
<script>
function findPosX(obj)
{
	var curleft = 0;
	if (obj.offsetParent)
	{
		while (obj.offsetParent)
		{
			curleft += obj.offsetLeft
			obj = obj.offsetParent;
		}
	}
	else if (obj.x)
		curleft += obj.x;
	return curleft;
}

function findPosY(obj)
{
	var curtop = 0;
	if (obj.offsetParent)
	{
		while (obj.offsetParent)
		{
			curtop += obj.offsetTop
			obj = obj.offsetParent;
		}
	}
	else if (obj.y)
		curtop += obj.y;
	return curtop;
}
</script>
</head>
<body onLoad="moveLines()">
<div id="navigation">
<a href="/about.html">About</a> &nbsp; &nbsp; <a href="/changes.cgi">Changes</a> &nbsp; &nbsp; <a href="/edit.html">Editing</a><br>
<a href="/legend.html">Legend</a> &nbsp; &nbsp; 
EOHTML
for ( 1..16 ) {
    print qq{<a href="?level=$_">$_</a> &nbsp; &nbsp; };
}
print <<EOHTML ;
</div>
Javatar - Level $level<br>
EOHTML
    
print <<EOHTML;
<table cellspacing="0" cellpadding="0" border="0">
<tr><td>
<div style="float: left">
Revision #$version
</div>
EOHTML
if ( $changed_rooms ) {
    my $rooms = ($changed_rooms>1)?'Rooms':'Room';
    print <<EOHTML;
<div style="float: left; border: solid black 1px; margin-left: 30px; padding-left: 10px; padding-right: 10px;">
$changed_rooms Updated $rooms<br>
<form action="regen.cgi" method="POST" onSubmit="document.getElementById('loading').style.display = ''">
<input type="hidden" name="level" value="$level">
<input type="hidden" name="x" value="$x">
<input type="hidden" name="y" value="$y">
<input type="submit" value="Regenerate Map">
</form>
</div>
EOHTML
}

print <<EOHTML;
<div style="float: right">
EOHTML
print_teleporters( $dbh, $level, $version );
print "</div></td></tr><tr><td>";
my $paddedlevel = $level;
if (length(sprintf "%d", $level) < 2) {
    $paddedlevel = '0'.$level;
}
printf qq{<img id="map" src="/maps/map_%s_v%d.png" width="710" height="710">}, $paddedlevel, $version;
if ( $x and $y ) {
    my $top_offset = 14;
    my $top = ((30-$q->param('y')) * 21) + $top_offset + 35;
    my $left = (($q->param('x')-1) * 21) + 50;
    print <<EOHTML;
<img id="hline1" src="/hline.png" style="position: absolute; visibility: hidden; top: 0; left: 0;" width="690" height="2">
<img id="hline2" src="/hline.png" style="position: absolute; visibility: hidden; top: 0; left: 0;" width="690" height="2">
<img id="vline1" src="/vline.png" style="position: absolute; visibility: hidden; top: 0; left: 0;" height="680" width="2">
<img id="vline2" src="/vline.png" style="position: absolute; visibility: hidden; top: 0; left: 0;" height="680" width="2">
<script>
function moveLines() {
    var map = document.getElementById('map');
    var hline1 = document.getElementById('hline1');
    var vline1 = document.getElementById('vline1');
    var hline2 = document.getElementById('hline2');
    var vline2 = document.getElementById('vline2');

    hline1.style.top = findPosY(map) + $top;
    hline1.style.left = findPosX(map) + 10;
    hline1.style.width = $left - 20;

    hline2.style.top = findPosY(map) + $top;
    hline2.style.left = findPosX(map) + $left +11;
    hline2.style.width = 690 - $left;

    vline1.style.top = findPosY(map) + 10;
    vline1.style.left = findPosX(map) + $left;
    vline1.style.height = $top - 20;

    vline2.style.top = findPosY(map) + $top + 12;;
    vline2.style.left = findPosX(map) + $left;
    vline2.style.height = 680 - $top + 10;

    hline1.style.visibility = '';
    vline1.style.visibility = '';
    hline2.style.visibility = '';
    vline2.style.visibility = '';
}
</script>
EOHTML
}
print <<EOHTML;
<div id="loading" style="position: absolute; left: 300px; top: 200px; display: none; background: #dfdfdf; border: solid black 2px; padding: 1em;">
<h2>Loading, please wait...</h2>
</div>
<script>
function map_click(e) {
    if (!e) var e = window.event;
    var target = e.target;
    if (!target) target = e.srcElement;
    var targetX = findPosX(target);
    var targetY = findPosY(target);
    var posx = 0;
    var posy = 0;
    if (e.pageX || e.pageY) {
        posx = e.pageX;
	posy = e.pageY;
    } else if (e.clientX || e.clientY) {
	posx = e.clientX + document.body.scrollLeft;
	posy = e.clientY + document.body.scrollTop;
    }
    var clx = Math.floor( (posx - targetX - 40) / 21 ) + 1;
    var cly = 30 - Math.floor( (posy - targetY - 40) / 21 );
    if ( clx > 0 && clx <= 30 && cly > 0 && cly <= 30 ) {
        if ( e.shiftKey ) {
            var tx = document.getElementById('tx');
            var ty = document.getElementById('ty');
            if ( tx && ty ) {
                tx.value = clx;
                ty.value = cly;
                updateDest();
            }
        } else {
            document.getElementById('loading').style.display = '';
            document.location = '?level=$level&x='+clx+'&y='+cly;
        }
    }
}

var map = document.getElementById('map');
map.onclick = map_click;
</script>
EOHTML
print "</td><td valign='top'>";
if ( $room ) {
    print <<EOHTML;
<h1>Edit $$room{'x'},$$room{'y'},$$room{'level'}</h1>
<form action="update_map.cgi" method="POST">
<input type="hidden" name="level" value="$level">
<input type="hidden" name="x" value="$x">
<input type="hidden" name="y" value="$y">
<style>
table, tr, td {
  margin: 0; padding: 0;
}
</style>
EOHTML
    if ( ! $$room{'version'} ) {
        print "<b>This room has been modified.</b>\n";
    }
    print "<table><tr><td></td><td><label>North<br>";
    select_list( 'north', [qw( wall open door secret )] );
    print "</label></td></tr><td><label>West<br>";
    select_list( 'west', [qw( wall open door secret )] );
    print "</label></td><td></td><td><label>East<br>";
    select_list( 'east', [qw( wall open door secret )] );
    print "</label></td></tr><tr><td></td><td><label>South<br>";
    select_list( 'south', [qw( wall open door secret )] );
    print "</label></td></tr></table>\n";
    print "<table>";
    print "<tr><td><label for='env'>Environment:</label></td><td>";
    select_list( 'env', [qw( normal rock pit water quicksand chute1 chute2 chute3 )] );
    print "</td></tr>\n";
    print "<tr><td><label for='facer'>Facer:</label></td><td>";
    select_list( 'facer', [qw( none up down left right random )] );
    print "</td></tr>\n";
    print "<tr><td><label for='special_mon'>Special encounters:</label></td><td>";
    select_list( 'special_mon', [qw( none giant dragon slime stud )] );
    print "</td></tr>\n";
    print "<tr><td><label for='movement'>Movement:</label></td><td>";
    select_list( 'movement', [qw( none stairsup stairsdown blink tp transup transdown randtp )] );
    print "</td></tr></table>\n";
    print "<label for='tx'>Teleport coordinates:</label><br><i><small>(only of \"tp\" selected above)</small></i><br>\n";
    print qq[<label>X: <input size="3" name="tx" id="tx" value="$$room{'tx'}"></label> ];
    print qq[<label>Y: <input size="3" name="ty" value="$$room{'ty'}"></label> ];
    print qq[<label>Z: <input size="3" name="tz" value="$$room{'tz'}"></label>];
    print qq[<br>\n];
    print "<label>"; checkbox( 'dark' ); print " Dark?</label><br>";
    print "<label>"; checkbox( 'nomagic' ); print " No magic?</label><br>";
    print "<label>"; checkbox( 'illusion' ); print " Illusion?</label><br>";
    print "<label>"; checkbox( 'exting' ); print " Extinguisher?</label><br>";
    print "<label>"; checkbox( 'traps' ); print " Various Traps?</label><br>";
    print qq[<input type="submit" value="Make Changes">];
    print "</form>";
} else {
    print <<EOHTML;
<style>
\@media screen {
    #legend { position: relative; top: 20; left: -20; }
}
\@media print {
    #legend { display: none; }
}
</style>
<img id="legend" src="/legend.png" width="200" height="670">
EOHTML
}
print <<EOHTML;
</td></tr></table>
<br clear="all">
</body>
</html>
EOHTML

sub select_list {
    my( $attr, $options ) = @_;
    print qq{<select id="$attr" name="$attr">};
    foreach ( @$options ) {
        print "<option";
        if ( $_ eq $$room{$attr} ) {
            print " selected";
        }
        print ">$_</option>";
    }
    print qq{</select>};
}
sub checkbox {
    my( $attr ) = @_;
    print qq{<input type="checkbox" value="1" name="$attr"};
    if ( $$room{$attr} ) {
        print " checked";
    }
    print ">";
}

sub print_teleporters {
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
    }
    print <<EOHTML;
<script>
function opentpv(x,y,z,v) {
    document.location = '?level='+z+'&x='+x+'&y='+y+'&version='+v;
}
function opentp(x,y,z) {
    document.location = '?level='+z+'&x='+x+'&y='+y;
}
hl = new Array;
function showSources(src) {
    for (var img in hl) {
        document.body.removeChild(hl[img]);
    }
    hl = new Array;
    var map = document.getElementById('map');
    for (a in src) {
        var x = src[a]['x'];
        var y = src[a]['y'];
        var l = src[a]['z'];
        var img = document.createElement('img');
        document.body.appendChild( img );
        img.src = '/highlight.gif';
        img.style.position = 'absolute';
        img.style.width = 20;
        img.style.height = 20;
        img.style.left = findPosX(map) + ((x-1) * 21) + 41;
        img.style.top  = findPosY(map) + ((30-y) * 21 ) + 40;
        hl.push(img);
    }
}
</script>
<style>
.targ { text-align: right; cursor: pointer; border-bottom: solid blue 1px; color: blue; }
.src { cursor: help; }
</style>
<table style="border: solid black 1px; width: 16em;">
<tr>
<td style="border-right: solid black 1px; width: 1em;">T<br>P</td>
<td style="width: 8em" valign="top">
EOHTML
    my $internal = <<EOHTML;
<table cellspacing="0" cellpadding="0" border="0">
EOHTML
    print $internal;
    for ( my $num = 0; $num < @tp; $num ++ ) {
        my $target;
        if ( $tp[$num]{'tz'} ne $level or !$q->param('version')) {
            $target = "opentp($tp[$num]{'tx'},$tp[$num]{'ty'},$tp[$num]{'tz'})";
        } else {
            $target = "opentpv($tp[$num]{'tx'},$tp[$num]{'ty'},$tp[$num]{'tz'},$version)";
        }
        my $hash = "$tp[$num]{'tx'},$tp[$num]{'ty'},$tp[$num]{'tz'}";
        my $source = join ', ', map { "{'x':$$_{'x'},'y':$$_{'y'},'z':$$_{'level'}}" } @{$tp{$hash}};
        printf qq{<tr><td class="src" onmouseover="showSources([$source]);">%d:</td>},$num+1;
        printf qq{<td>&nbsp;<span class="targ" onmouseover="showSources([$source]);" onclick="$target">→</span></td>}.
            qq{<td class="targ" onmouseover="showSources([$source]);" onclick="$target">%d,</td>}.
            qq{<td class="targ" onmouseover="showSources([$source]);" onclick="$target">%d</td>},
            $tp[$num]{'tx'},$tp[$num]{'ty'};
        if ( $tp[$num]{'tz'} ne $level ) {
            printf qq{<td class="targ" onmouseover="showSources([$source]);" onclick="$target">,%2d</td>}, $tp[$num]{'tz'};
        }
        print "</tr>\n";
        if ( $num % 2 and $num < 2 ) {
            print qq{</table></td><td style="width: 7em;" valign="top">$internal};
        }
    }
    print qq{</table></td></tr></table>};
}
