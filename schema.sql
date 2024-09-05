Create Table: CREATE TABLE levels (
  id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  num VARCHAR(10) NOT NULL DEFAULT '0',
  version INT(11) NOT NULL DEFAULT '0',
  created DATETIME NOT NULL DEFAULT '0000-00-00 00:00:00',
  whom VARCHAR(40) NOT NULL DEFAULT ''
);

CREATE TABLE map (
  id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  level varchar(10) NOT NULL DEFAULT '0',
  x int(11) NOT NULL DEFAULT '0',
  y int(11) NOT NULL DEFAULT '0',
  movement enum('stairsup','stairsdown','blink','tp','transup','transdown','randtp','none') NOT NULL DEFAULT 'none',
  env enum('rock','pit','water','quicksand','chute1','chute2','chute3','normal') NOT NULL DEFAULT 'normal',
  dark int(11) NOT NULL DEFAULT '0',
  nomagic int(11) NOT NULL DEFAULT '0',
  facer enum('none','up','down','left','right','random') NOT NULL DEFAULT 'none',
  illusion int(11) NOT NULL DEFAULT '0',
  special_mon enum('giant','dragon','slime','stud','superstud','none') NOT NULL DEFAULT 'none',
  north enum('open','door','secret','wall') NOT NULL DEFAULT 'wall',
  south enum('open','door','secret','wall') NOT NULL DEFAULT 'wall',
  east enum('open','door','secret','wall') NOT NULL DEFAULT 'wall',
  west enum('open','door','secret','wall') NOT NULL DEFAULT 'wall',
  tx int(11) DEFAULT NULL,
  ty int(11) DEFAULT NULL,
  exting int(11) NOT NULL DEFAULT '0',
  tz varchar(10) DEFAULT NULL,
  traps int(11) NOT NULL DEFAULT '0',
  tpmeta int(11) DEFAULT NULL, -- I have no idea what this was for, it's only referenced to ignore it, but some rows have values.... ?!
  version int(11) DEFAULT NULL,
  start datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  end datetime NOT NULL DEFAULT '9999-12-31 23:59:59',
  KEY x (x),
  KEY y (y),
  KEY version (version)
);
