LON1=142:11:57
LON2=142:12:04
LAT1=44:18:14
LAT2=44:18:20

sed "1d" MargeObs.txt | awk -F"\t" '{print $3,$2,$5-$4}' > tmp.txt
gmt nearneighbor tmp.txt -R${LON1}/${LON2}/${LAT1}/${LAT2} -S5e -I1e -Ga.grd

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
    gmt grdcontour ${GRD} -C1 -A5+f6,Helvetica -Gd4
    gmt plot loc.txt -Sx0.3 -W2,180/60/60
    gmt colorbar -Bxf1a5+l"depth (m)" -C${CPT}
gmt end show