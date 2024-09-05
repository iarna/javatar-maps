// These two functions find the display location of an object in the
// document in a browser independent manner.

function findPosX(obj) {
    var curleft = 0;
    if (obj.offsetParent) {
        while (obj.offsetParent) {
            curleft += obj.offsetLeft
            obj = obj.offsetParent;
        }
    } else if (obj.x) {
        curleft += obj.x;
    }
    return curleft;
}

function findPosY(obj) {
    var curtop = 0;
    if (obj.offsetParent) {
        while (obj.offsetParent) {
            curtop += obj.offsetTop
            obj = obj.offsetParent;
        }
    } else if (obj.y) {
        curtop += obj.y;
    }
    return curtop;
}

function opentpv(x,y,z,v) {
    document.location = '?level='+z+'&x='+x+'&y='+y+'&version='+v;
}

function opentp(x,y,z) {
    document.location = '?level='+z+'&x='+x+'&y='+y;
}

function highlightTP(x,y,z) {
    document.getElementById('tp'+x+'_'+y+'_'+z).style.background = 'yellow';
}

function unhighlightTP(x,y,z) {
    document.getElementById('tp'+x+'_'+y+'_'+z).style.background = '';
}


function Avatar( level, x, y, tpl ) {
    this.hl = new Array;
    this.tpl = tpl;
    this.level = level;
    this.x = x;
    this.y = y;
    this.last_x = 0;
    this.last_y = 0;
    this.moveLines = moveLines;
    this.showSources = showSources;
    this.updateDest = updateDest;
    this.map = document.getElementById('map');
    this.sel = document.getElementById('selector');
    if ( this.x && this.y ) {
        this.moveLines();
    }
    this.map.onmousemove = map_mousemove;
    this.map.onclick = map_click;
    this.sel.onmousemove = map_mousemove;
    this.sel.onclick = map_click;
}


function showSources(src) {
    for (var img in this.hl) {
        document.body.removeChild(this.hl[img]);
    }
    this.hl = new Array;
    for (a in src) {
        var x = src[a]['x'];
        var y = src[a]['y'];
        var l = src[a]['z'];
        var img = document.createElement('img');
        img.src = 'highlight.gif';
        img.style.position = 'absolute';
        img.style.width = '20px';
        img.style.height = '20px';
        img.style.left = (findPosX(this.map) + ((x-1) * 21) + 41) + 'px';
        img.style.top  = (findPosY(this.map) + ((30-y) * 21 ) + 40) + 'px';
        img.onmousemove = map_mousemove;
        img.onclick = map_click;
        this.hl.push(img);
        document.body.appendChild( img );
    }
}



function moveLines() {
    var map = this.map;
    var hline1 = document.getElementById('hline1');
    var vline1 = document.getElementById('vline1');
    var hline2 = document.getElementById('hline2');
    var vline2 = document.getElementById('vline2');
    var selector = this.sel;

    var top_offset = 14;
    var top = ((30-this.y) * 21) + top_offset + 35;
    var left = ((this.x-1) * 21) + 50;

    var my = findPosY(map);
    var mx = findPosX(map);

    var htop = (my + top) + 'px';
    var vleft = (mx + left) + 'px';

    hline1.style.top = htop;
    hline1.style.left = (mx + 10) + 'px';
    hline1.style.width = (left - 20) + 'px';

    hline2.style.top = htop;
    hline2.style.left = (mx + left +11) + 'px';
    hline2.style.width = (690 - left) + 'px';

    vline1.style.top = (my + 10) + 'px';
    vline1.style.left = vleft;
    vline1.style.height = (top - 20) + 'px';

    vline2.style.top = (my + top + 12) + 'px';;
    vline2.style.left = vleft;
    vline2.style.height = (680 - top + 10) + 'px';

    selector.style.left = (mx + left - 9) + 'px';
    selector.style.top  = (my + top - 8) + 'px';
    selector.style.display='block';

    hline1.style.display = 'block';
    vline1.style.display = 'block';
    hline2.style.display = 'block';
    vline2.style.display = 'block';
}

function updateDest() {
    var dir = document.getElementById('dir').value;
    var tx = document.getElementById('tx').value;
    var ty = document.getElementById('ty').value;
    var ahead = document.getElementById('ahead');
    var right = document.getElementById('right');
    var map = document.getElementById('map');
    var sel = document.getElementById('selector');
    sel.style.left = ((tx-1)*21 + findPosX(map) + 41) + 'px';
    sel.style.top = ((30-ty)*21 + findPosY(map) + 41) + 'px';
    sel.style.display='block';
    if ( dir && tx && ty ) {
        if ( dir == 'North' ) {
            ahead.value = ty - this.y;
            right.value = tx - this.x;
        } else if ( dir == 'South' ) {
            ahead.value = this.y - ty;
            right.value = this.x - tx;
        } else if ( dir == 'West' ) {
            ahead.value = this.x - tx;
            right.value = ty - this.y;
        } else if ( dir == 'East' ) {
            ahead.value = tx - this.x;
            right.value = this.y - ty;
        }
    }
}



function map_mousemove(e) {
    if (!e) var e = window.event;
    var avatar = window.avatar;
    if ( ! avatar ) {
        return;
    }
    var map = avatar.map;
    var mapX = findPosX(map);
    var mapY = findPosY(map);
    var posx = 0;
    var posy = 0;
    if (e.pageX || e.pageY) {
        posx = e.pageX;
	posy = e.pageY;
    } else if (e.clientX || e.clientY) {
	posx = e.clientX + document.body.scrollLeft;
	posy = e.clientY + document.body.scrollTop;
    }
    var clx = Math.floor( (posx - mapX - 40 ) / 21 ) + 1;
    var cly = 30 - Math.floor( (posy - mapY - 40) / 21 );
    if ( avatar.tpl[ '/' + avatar.last_x + ',' + avatar.last_y ] &&
         (clx != avatar.last_x || cly != avatar.last_y) ) {
         var tp = avatar.tpl[ '/' + avatar.last_x + ',' + avatar.last_y ];
         unhighlightTP( tp['x'], tp['y'], tp['z'] );
         avatar.showSources([]);
         avatar.last_x = 0;
         avatar.last_y = 0;
    }
    if ( clx > 0 && clx <= 30 && cly > 0 && cly <= 30 ) {
        if ( avatar.tpl[ '/' + clx + ',' + cly ] &&
             ( avatar.last_x != clx || avatar.last_y != cly) ) {
            var tp = avatar.tpl[ '/' + clx + ',' + cly ];
            highlightTP( tp['x'], tp['y'], tp['z'] );
            if ( tp['z'] == avatar.level ) {
                avatar.showSources( [{'x':tp['x'], 'y':tp['y']}] );
            }
            avatar.last_x = clx;
            avatar.last_y = cly;
        }
        if ( e.shiftKey ) {
            var tx = document.getElementById('tx');
            var ty = document.getElementById('ty');
            if ( tx && ty ) {
                tx.value = clx;
                ty.value = cly;
                avatar.updateDest();
            }
        }
    }
}
function map_click(e) {
    if (!e) var e = window.event;
    var avatar = window.avatar;
    var map = document.getElementById('map');
    var mapX = findPosX(map);
    var mapY = findPosY(map);
    var posx = 0;
    var posy = 0;
    if (e.pageX || e.pageY) {
        posx = e.pageX;
	posy = e.pageY;
    } else if (e.clientX || e.clientY) {
	posx = e.clientX + document.body.scrollLeft;
	posy = e.clientY + document.body.scrollTop;
    }
    var clx = Math.floor( (posx - mapX - 40) / 21 ) + 1;
    var cly = 30 - Math.floor( (posy - mapY - 40) / 21 );
    if ( clx > 0 && clx <= 30 && cly > 0 && cly <= 30 ) {
        document.getElementById('loading').style.display = '';
        document.location = '?level='+avatar.level+'&x='+clx+'&y='+cly;
    }
}
