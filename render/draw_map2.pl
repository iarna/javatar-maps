#!/usr/bin/perl
use DBI;
use SVG;
use strict;
use warnings;
use vars qw( $tile_size $room_size $margin $wall_width %c %icons %tp $tp );
my $dbh = DBI->connect('dbi:mysql:database=javatar', 'avatar', 'WRENtlal');

my( $level, $version, $file ) = @ARGV;
if ( !$file ) {
    die "Usage: $0 level version file\n";
}

$tile_size = 30;
$room_size = 20;
$margin = 40;
$wall_width = 1;

my $size = $margin*2 + $tile_size*($room_size+$wall_width);
my $im = SVG->new(width=>$size, height=>$size,
    'xmlns' => "http://www.w3.org/2000/svg"
    );

$icons{'transdown'}  = 'transdown.png';
$icons{'transup'}    = 'transup.png';
$icons{'extinguish'} = 'extinguish.png';
$icons{'dark'} = 'dark.png';
$icons{'illusion'} = 'illusion.png';
$icons{'water'} = 'water.png';
$icons{'pit'} = 'pit.png';
$icons{'tp1'} = 'tp1.png';
$icons{'tp2'} = 'tp2.png';
$icons{'tp3'} = 'tp3.png';
$icons{'tp4'} = 'tp4.png';
$icons{'tp5'} = 'tp5.png';
$icons{'randtp'} = 'randtp.png';
$icons{'rotator'} = 'rotator.png';
$icons{'stairsup'} = 'stairsup.png';
$icons{'stairsdown'} = 'stairsdown.png';
$icons{'stud'} = 'stud.png';
$icons{'chute1'} = 'chute1.png';
$icons{'chute2'} = 'chute2.png';
$icons{'chute3'} = 'chute3.png';
$icons{'faceleft'} = 'faceleft.png';
$icons{'faceright'} = 'faceright.png';
$icons{'faceup'} = 'faceup.png';
$icons{'facedown'} = 'facedown.png';
$icons{'slime'} = 'slime.png';
$icons{'dragon'} = 'dragon.png';
$icons{'giant'} = 'giant.png';
$icons{'blink'} = 'blink.png';
$icons{'quicksand'} = 'quicksand.png';
$icons{'traps'} = 'traps.png';

$im->rectangle( x=> 0, y=> 0, width=> $size, height=> $size, fill=>'white');




my $grid = $im->group( style=> {
    'stroke'=>'rgb(200,200,200)',
    'stroke-width'=>.35,
     } );

my $map_svg = $im->group(
    id => 'map_group',
    style => {
        'stroke'=>'black',
        fill=>'white',
        'stroke-width'=>1,
        'font'      => 'sans',
        'font-size' => '14',
        },
    );

for ( 1..$tile_size+1 ) {
    my $start = $margin - ( ($room_size + $wall_width) );
    my $end   = $start+ (( $room_size + $wall_width ) * ($tile_size+2));
    my $line = $margin + ( ($_-1) * ( $room_size + $wall_width ) );
    $grid->line( x1=>$start, x2=>$end,  y1=>$line, y2=>$line );
    $grid->line( y1=>$start, y2=>$end,  x1=>$line, x2=>$line );
}

my $map;
if ( $version ) {
    my $sth = $dbh->prepare(<<EOSQL);
SELECT created FROM levels where num=? AND version=?
EOSQL
    $sth->execute( $level, $version );
    my( $created ) = $sth->fetchrow_array;
    $map = $dbh->prepare(<<EOSQL);
SELECT * FROM map WHERE level=? AND 
    ( version=? OR  
      ( version IS NOT NULL AND start < ? AND end > ? )
    )
ORDER BY y,x
EOSQL
    $map->execute( $level, $version, $created, $created );
    while ( my $room = $map->fetchrow_hashref ) {
        draw_room( $map_svg, $room );
    }
}

my $bump_it_x = $wall_width * 2;
my $bump_it_y = $wall_width * 4;
for ( 1..$tile_size ) {
    # X coordinates across top
    $map_svg->text(
        style=>{stroke=> ($_ % 2) ? 'black' : 'rgb(127,127,127)' },
        x=>$margin+(($_-1)*($room_size+$wall_width))+$bump_it_x, 
        y=>$margin-($room_size/2) + $bump_it_y,
        -cdata=>sprintf("%02d",$_),
        );
    # X coordinates across bottom
    $map_svg->text(
        style=>{stroke=> ($_ % 2) ? 'black' : 'rgb(127,127,127)' },
        x=>$margin+(($_-1)*($room_size+$wall_width))+$bump_it_x, 
        y=>$margin+(($room_size+$wall_width)*$tile_size)+$room_size - $bump_it_x*3,
        -cdata=>sprintf("%02d",$_),
        );
    my $ytext = 31-$_;
    # Y coordinates across left
    $map_svg->text(
        style=>{stroke=> ($_ % 2) ? 'black' : 'rgb(127,127,127)' },
        y=>$margin+(($_-1)*($room_size+$wall_width))+($room_size/2)+$bump_it_y, 
        x=>$margin-$room_size,
        -cdata=>sprintf("%02d",$ytext),
        );
    # Y coordinates across right
    $map_svg->text(
        style=>{stroke=> ($_ % 2) ? 'black' : 'rgb(127,127,127)' },
        y=>$margin+(($_-1)*($room_size+$wall_width))+($room_size/2)+$bump_it_y, 
        x=>$margin+(($room_size+$wall_width)*$tile_size)+($room_size/2)-$bump_it_x*3,
        -cdata=>sprintf("%02d",$ytext),
        );
}

open( OUT, ">$file" )
   or die "Could not open $file: $!\n";
print OUT $im->xmlify;
close OUT
   or die "Could not write $file: $!\n";


sub draw_room {
    my( $im, $room ) = @_;
    my $ix = $margin + ( ($$room{'x'} - 1) * ($room_size + $wall_width) );
    my $iy = $margin + ( ($tile_size - $$room{'y'}) * ($room_size + $wall_width) );
    my $full_size = $room_size + $wall_width;
#    my $img_size = $room_size - $wall_width*3;
#    my $img_top  = $iy + $wall_width;
#    my $img_left = $ix + $wall_width;
    my $img_size = $room_size - $wall_width*2;
    my $img_top = $iy + $wall_width*2;
    my $img_left = $ix + $wall_width*2;
    my $full = 0;
    if ( $$room{'env'} eq 'rock' ) {
        $im->rectangle(
            x => $ix, y => $iy-$wall_width, width => $full_size, height => $full_size, 
            style => {
                fill  => 'black',
            });
        $full = 1;
    } elsif ( $$room{'env'} eq 'water' ) {
        $im->image(
            x => $ix, y => $iy-$wall_width, width => $full_size, height=>$full_size,
            '-href' => $icons{'water'},
            );
        $full = 1;
    } elsif ( $$room{'env'} eq 'quicksand' ) {
        $im->image(
            x => $ix, y => $iy-$wall_width, width => $full_size, height=>$full_size,
            '-href' => $icons{'quicksand'},
            );
        $full = 1;
    }
    if ( $$room{'dark'} ) {
        $im->image(
            x => $ix, y => $iy-$wall_width, width => $full_size, height=>$full_size,
            '-href' => $icons{'dark'},
            );
        $full = 1;
          
    }
    if ( $$room{'special_mon'} eq 'stud' ) {
        $im->image(
            x => $ix, y => $iy-$wall_width, width => $full_size, height=>$full_size,
            '-href' => $icons{'stud'},
            );
        $full = 1;
    } elsif ( $$room{'special_mon'} eq 'slime' ) {
        $im->image(
            x => $ix, y => $iy-$wall_width, width => $full_size, height=>$full_size,
            '-href' => $icons{'slime'},
            );
    } elsif ( $$room{'special_mon'} eq 'giant' ) {
        $im->image(
            x => $ix, y => $iy-$wall_width, width => $full_size, height=>$full_size,
            '-href' => $icons{'giant'},
            );
    } elsif ( $$room{'special_mon'} eq 'dragon' ) {
        $im->image(
            x => $ix, y => $iy-$wall_width, width => $full_size, height=>$full_size,
            '-href' => $icons{'dragon'},
            );
    } elsif ( $$room{'special_mon'} eq 'none' ) {
        # Nothing
    } else {
       die "Unknown special monster type: $$room{'special_mon'}\n";
    }
    if ( $$room{'env'} eq 'pit' ) {
        $im->image(
            x => $img_left, y => $img_top, width => $img_size, height=>$img_size,
            '-href' => $icons{'pit'},
            );
    } elsif ( $$room{'env'} eq 'chute1' ) {
        $im->image(
            x => $img_left, y => $img_top, width => $img_size, height=>$img_size,
            '-href' => $icons{'chute1'},
            );
    } elsif ( $$room{'env'} eq 'chute2' ) {
        $im->image(
            x => $img_left, y => $img_top, width => $img_size, height=>$img_size,
            '-href' => $icons{'chute2'},
            );
    } elsif ( $$room{'env'} eq 'chute3' ) {
        $im->image(
            x => $img_left, y => $img_top, width => $img_size, height=>$img_size,
            '-href' => $icons{'chute3'},
            );
    } elsif ( $$room{'env'} eq 'normal' ) {
        # Nothing
    } else {
#        die "Unknown environment: $$room{'env'}\n";
    }
    if ( $$room{'traps'} ) {
        $im->image(
            x => $img_left, y => $img_top, width => $img_size, height=>$img_size,
            '-href' => $icons{'traps'},
            );
    }
    if ( $$room{'illusion'} ) {
        $im->image(
            x => $img_left, y => $img_top, width => $img_size, height=>$img_size,
            '-href' => $icons{'illusion'},
            );
    }
    if ( $$room{'movement'} eq 'transdown' ) {
        $im->image(
            x => $img_left, y => $img_top, width => $img_size, height=>$img_size,
            '-href' => $icons{'transdown'},
            );
    } elsif ( $$room{'movement'} eq 'transup' ) {
        $im->image(
            x => $img_left, y => $img_top, width => $img_size, height=>$img_size,
            '-href' => $icons{'transup'},
            );
    } elsif ( $$room{'movement'} eq 'stairsdown' ) {
        $im->image(
            x => $img_left, y => $img_top, width => $img_size, height=>$img_size,
            '-href' => $icons{'stairsdown'},
            );
    } elsif ( $$room{'movement'} eq 'stairsup' ) {
        $im->image(
            x => $img_left, y => $img_top, width => $img_size, height=>$img_size,
            '-href' => $icons{'stairsup'},
            );
    } elsif ( $$room{'movement'} eq 'tp' ) {
        if ($room->{level} and $room->{tx} and $room->{ty} and $room->{tz}) {
            my $hash = "$$room{'level'},$$room{'tx'},$$room{'ty'},$$room{'tz'}";
            my $num = $tp{$hash} || ( $tp{$hash} = ++ $tp );
            $im->image(
                x => $img_left, y => $img_top, width => $img_size, height=>$img_size,
                '-href' => $icons{"tp$num"},
                );
        }
    } elsif ( $$room{'movement'} eq 'randtp' ) {
        $im->image(
            x => $img_left, y => $img_top, width => $img_size, height=>$img_size,
            '-href' => $icons{'randtp'},
            );
    } elsif ( $$room{'movement'} eq 'blink' ) {
        $im->image(
            x => $img_left, y => $img_top, width => $img_size, height=>$img_size,
            '-href' => $icons{'blink'},
            );
    } elsif ( $$room{'movement'} eq 'none' ) {
    } else {
        die "Unknown movement type: $$room{'movement'}\n";
    }
    if ( $$room{'exting'} ) {
        $im->image(
            x => $img_left, y => $img_top, width => $img_size, height=>$img_size,
            '-href' => $icons{'extinguish'},
            );
    }
    if ( $$room{'facer'} eq 'up' ) {
        $im->image(
            x => $img_left, y => $img_top, width => $img_size, height=>$img_size,
            '-href' => $icons{'faceup'},
            );
    } elsif ( $$room{'facer'} eq 'down' ) {
        $im->image(
            x => $img_left, y => $img_top, width => $img_size, height=>$img_size,
            '-href' => $icons{'facedown'},
            );
    } elsif ( $$room{'facer'} eq 'left' ) {
        $im->image(
            x => $img_left, y => $img_top, width => $img_size, height=>$img_size,
            '-href' => $icons{'faceleft'},
            );
    } elsif ( $$room{'facer'} eq 'right' ) {
        $im->image(
            x => $img_left, y => $img_top, width => $img_size, height=>$img_size,
            '-href' => $icons{'faceright'},
            );
    } elsif ( $$room{'facer'} eq 'random' ) {
        $im->image(
            x => $img_left, y => $img_top, width => $img_size, height=>$img_size,
            '-href' => $icons{'rotator'},
            );
    } elsif ( $$room{'facer'} eq 'none' ) {
        # Nothing
    } else {
        die "Unknown facer type: $$room{'facer'}\n";
    }

    if ( $$room{'nomagic'} ) {
        my $margin = 1;
        my $chunk_width = ($room_size-($margin*2)-2)/3;
        my $top = $iy + $margin + 1;
        my $bottom = $top + $chunk_width*3;
        my $left = $ix + $margin + 1;
        my $right = $left + $chunk_width*3;
        # Top left horizontal line
        $im->line( x1 => $left, x2=> $left + $chunk_width, y1=>$top,y2=>$top );
        # Top right horizontal line
        $im->line( x1 => $right, x2=> $right - $chunk_width, y1=>$top,y2=>$top );
        # Bottom left horizontal line
        $im->line( x1 => $left, x2=> $left + $chunk_width, y1=>$bottom,y2=>$bottom );
        # Bottom right horizontal line
        $im->line( x1 => $right, x2=> $right - $chunk_width, y1=>$bottom,y2=>$bottom );
        # Left top vertical line
        $im->line( y1 => $top, y2=> $top + $chunk_width, x1=>$left,x2=>$left );
        # Left bottom vertical line
        $im->line( y1 => $bottom, y2=> $bottom - $chunk_width, x1=>$left,x2=>$left );
        # Right top vertical line
        $im->line( y1 => $top, y2=> $top + $chunk_width, x1=>$right,x2=>$right );
        # Right bottom vertical line
        $im->line( y1 => $bottom, y2=> $bottom - $chunk_width, x1=>$right,x2=>$right );
        
    }

    draw_hwall( $im, $$room{'south'}, $ix-$wall_width, $iy+$room_size );
    draw_hwall( $im, $$room{'north'}, $ix-$wall_width, $iy-$wall_width );

    draw_vwall( $im, $$room{'west'}, $ix-$wall_width, $iy-$wall_width );
    draw_vwall( $im, $$room{'east'}, $ix+$room_size, $iy-$wall_width );
}

sub draw_hwall {
    my( $im, $type, $start, $rc ) = @_;
    my $full_size = $room_size+ $wall_width;
    my $di    = $full_size/3;
    my $ds    = $full_size/10;
    if ( $type eq 'door' ) {
        # Draw the first third of the wall
        draw_wall_line( $im, $start, $rc, 'x', $di );
        # Draw the last third of the wall
        draw_wall_line( $im, $start+(2*$di), $rc, 'x', ($full_size-(2*$di)) );
        # Draw the left line of the door
        draw_wall_line( $im, $start+$di, $rc-$ds, 'y', ($ds*2) );
        # Draw the right line of the door
        draw_wall_line( $im, $start+(2*$di), $rc-$ds, 'y', ($ds*2) );
    } elsif ( $type eq 'secret' ) {
        # Draw the first third of the wall
        draw_wall_line( $im, $start, $rc, 'x', $di );
        # Draw the last third of the wall
        draw_wall_line( $im, $start+(2*$di), $rc, 'x', ($full_size-(2*$di)) );

        $im->rectangle(
            x=> $start+$di,
            y=> $rc-$ds,
            width => $di,
            height => $ds*2,
            );
    } elsif ( $type eq 'wall' ) {
        draw_wall_line( $im, $start, $rc, 'x', $full_size );
    } elsif ( $type eq 'open' ) {
    } else {
        warn "Unknown wall type: $type\n";
    }
}
sub draw_vwall {
    my( $im, $type, $rc, $start ) = @_;
    my $full_size = $room_size+ $wall_width;
    my $di    = $full_size/3;
    my $ds    = $full_size/10;
    if ( $type eq 'door' ) {
        # Draw the first third of the wall
        draw_wall_line( $im, $rc, $start, 'y', $di );
        # Draw the last third of the wall
        draw_wall_line( $im, $rc, $start+(2*$di), 'y', ($full_size-(2*$di)) );
        # Draw the left line of the door
        draw_wall_line( $im, $rc-$ds, $start+$di, 'x', ($ds*2) );
        # Draw the right line of the door
        draw_wall_line( $im, $rc-$ds, $start+(2*$di), 'x', ($ds*2) );
    } elsif ( $type eq 'secret' ) {
        # Draw the first third of the wall
        draw_wall_line( $im, $rc, $start, 'y', $di );
        # Draw the last third of the wall
        draw_wall_line( $im, $rc, $start+(2*$di), 'y', ($full_size-(2*$di)) );

        $im->rectangle(
            x=> $rc-$ds,
            y=> $start+$di,
            width => $ds*2,
            height => $di,
            );
    } elsif ( $type eq 'wall' ) {
        draw_wall_line( $im, $rc, $start, 'y', $full_size );
    } elsif ( $type eq 'open' ) {
    } else {
        warn "Unknown wall type: $type\n";
    }
}

sub draw_wall_line {
    my( $im, $x1, $y1, $axis, $len) = @_;
    if ( $axis eq 'x' ) {
        $im->line( x1=> $x1, y1=>$y1, x2=>$x1+$len, y2=>$y1 );
    } else {
        $im->line( x1=> $x1, y1=>$y1, x2=>$x1, y2=>$y1+$len );
    }
}

__END__
newFromPng
newFromJpeg
newFromGif 
rectangle
getPixel(x,y)
setPixel(x,y,color)
line(x1,y1,x2,y2,color)
GD::Polygon
GD::Image
GD::Font
