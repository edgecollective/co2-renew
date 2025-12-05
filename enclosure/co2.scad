// CSG.scad - Basic example of CSG usage

x_shift=10;

plate_width=88+x_shift;
keyboard_height=54;
rook_height=44;
margin_between=20;
margin_above=20;
plate_height=keyboard_height+rook_height+margin_between+margin_above;

r_h1_x=0;
r_h1_y=0;
r_h2_x=72;
r_h2_y=44;
r_h3_x=0;
r_h3_y=44;


y_shift=keyboard_height+margin_between;
height=100;
BottomRadius=3;

projection() {
difference() {
cube(size=[plate_width,plate_height,2],center=false);

translate([x_shift,y_shift,0]) {
//r_h1:
translate([r_h1_x,r_h1_y,0])
cylinder(h = height, r = BottomRadius, center = true);

//r_h2:
translate([r_h2_x,r_h2_y,0])
cylinder(h = height, r = BottomRadius, center = true);

//r_h3:
translate([r_h3_x,r_h3_y,0])
cylinder(h = height, r = BottomRadius, center = true);
}

//keyboard hole
translate([x_shift,keyboard_height,0])
cylinder(h = height, r = BottomRadius, center = true);
}
}
/*
translate([-24,0,0]) {
    union() {
        cube(15, center=true);
        sphere(10);
    }
}

intersection() {
    cube(15, center=true);
    sphere(10);
}

translate([24,0,0]) {
    difference() {
        cube(15, center=true);
        cube(10, center=true);
    }
}
*/

echo(version=version());
// Written by Marius Kintel <marius@kintel.net>
//
// To the extent possible under law, the author(s) have dedicated all
// copyright and related and neighboring rights to this software to the
// public domain worldwide. This software is distributed without any
// warranty.
//
// You should have received a copy of the CC0 Public Domain
// Dedication along with this software.
// If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
