
(function (ph){
try{
var A = self['' || 'AdriverCounter'],
	a = A(ph);
a.reply = {
ph:ph,
rnd:'930610',
bt:62,
sid:224247,
pz:0,
sz:'%2f',
bn:0,
sliceid:0,
netid:0,
ntype:0,
tns:0,
pass:'',
adid:0,
bid:2864425,
geoid:12,
cgihref:'//ad.adriver.ru/cgi-bin/click.cgi?sid=224247&ad=0&bid=2864425&bt=62&bn=0&pz=0&xpid=DG8U3htca6wSgn58-Ao8eLj27LxQFo9bIhNqCK9SS6cXt_Q6b5XoGjakEMqjIpXi8zz97Pw3b4tmATfzkSbTJOEFRwQ&ref=https:%2f%2fdomclick.ru%2f&custom=',
target:'_blank',
width:'0',
height:'0',
alt:'AdRiver',
mirror:A.httplize('//mlb5.adriver.ru'), 
comp0:'0/script.js',
custom:{},
track_site:0,
cid:'AvVHfvIoP9shUqzEqCBL8ww',
uid:2485208720821,
xpid:'DG8U3htca6wSgn58-Ao8eLj27LxQFo9bIhNqCK9SS6cXt_Q6b5XoGjakEMqjIpXi8zz97Pw3b4tmATfzkSbTJOEFRwQ'
}
var r = a.reply;

r.comppath = r.mirror + '/images/0002864/0002864425/' + (/^0\//.test(r.comp0) ? '0/' : '');
r.comp0 = r.comp0.replace(/^0\//,'');
if (r.comp0 == "script.js" && r.adid){
	A.defaultMirror = r.mirror; 
	A.loadScript(r.comppath + r.comp0 + '?v' + ph) 
} else if ("function" === typeof (A.loadComplete)) {
   A.loadComplete(a.reply);
}
}catch(e){} 
}('1'));
