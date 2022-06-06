LON1=142:11:57
LON2=142:12:04
LAT1=44:18:14.5
LAT2=44:18:19.5

SEARCH=10e
INT=1e

sed "1d" MargeObs.txt | awk -F"\t" '{print $3,$2,$8-$4}' > tmp.txt
gmt nearneighbor tmp.txt -R${LON1}/${LON2}/${LAT1}/${LAT2} -S${SEARCH} -I${INT} -Ga.grd
# gmt surface tmp.txt -R${LON1}/${LON2}/${LAT1}/${LAT2} -I${INT} -Ga.grd

gmt makecpt -Chaxby -T-20/0/0.5 -D -Z > a.cpt

GRD='a.grd'
CPT='a.cpt'

echo '142.20 44.3049666667' > loc.txt

gmt gmtset MAP_FRAME_TYPE plain
gmt gmtset FONT_ANNOT_PRIMARY 10p,Helvetica
gmt gmtset FONT_LABEL 10p,Helvetica
gmt gmtset FONT_TITLE 10p,Helvetica
gmt gmtset FONT_LOGO 10p,Helvetica-Bold
gmt gmtset MAP_FRAME_PEN 1,black
gmt gmtset FORMAT_GEO_MAP F -V
gmt gmtset FORMAT_GEO_MAP ddd:mm:ssF

gmt begin a png
    gmt grdimage ${GRD} -R${LON1}/${LON2}/${LAT1}/${LAT2} -JM10 -BNWes -C${CPT} -Bxfa -Byfa
    gmt grdcontour ${GRD} -C0.5 -A5+f6,Helvetica -Gd4
    gmt plot loc.txt -Sx0.3 -W2,180/60/60
    gmt plot tmp.txt -Sc0.05 -G60/60/180
    gmt plot position.txt -Sc0.15 -W1,180/60/60 -G180/60/60
    gmt text position.txt -F+f6p,Helvetica-Bold+jRB
    gmt colorbar -Bxf1a5+l"depth (m)" -C${CPT}
gmt end show

gmt grdtrack position.txt -G${GRD} > out.txt

cp a.png LakeShumarinaiS${SEARCH}I${INT}.png