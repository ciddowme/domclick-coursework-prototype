
(function (ph){
try{
var A = self['' || 'AdriverCounter'],
	a = A(ph);
a.reply = {
ph:ph,
rnd:'263215',
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
cgihref:'//ad.adriver.ru/cgi-bin/click.cgi?sid=224247&ad=0&bid=2864425&bt=62&bn=0&pz=0&xpid=D_lBgeo9vX2Du0guaHBPykcXDR5f9phoxLy6FMhXVWg1Pk7bcGG4d-IFf1MuXJIndhBs-2cZ0E1O_fv8EzcBnNQBqqA&ref=https:%2f%2fdomclick.ru%2f&custom=',
target:'_blank',
width:'0',
height:'0',
alt:'AdRiver',
mirror:A.httplize('//mlb2.adriver.ru'), 
comp0:'0/script.js',
custom:{},
track_site:0,
cid:'AvVHfvIoP9shUqzEqCBL8ww',
uid:2485208720821,
xpid:'D_lBgeo9vX2Du0guaHBPykcXDR5f9phoxLy6FMhXVWg1Pk7bcGG4d-IFf1MuXJIndhBs-2cZ0E1O_fv8EzcBnNQBqqA'
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
