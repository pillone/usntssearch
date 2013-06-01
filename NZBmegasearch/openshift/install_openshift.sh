#~ OPENSHIFT_DATA_DIR
echo '*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*' 
echo '               NZBMEGASEARCH install for Openshift'
echo '*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*' 

echo 'Running update -- 01/02'
git fetch

echo 'Running update -- 02/02'
git reset --hard origin/master

echo 'Preparing...'
cp ../builtin_params.ini .

#~ SETS DEFAULT PWD
grep -v '^general_user' ../builtin_params.ini | grep -v '^general_pwd' > tmpfl.tmp
printf 'general_user = NZBMadmin\ngeneral_pwd = NZBMadmin\n' >> ../builtin_params.ini

cp ../builtin_params.ini $OPENSHIFT_DATA_DIR
cp ../vernum.num $OPENSHIFT_DATA_DIR
cp application $OPENSHIFT_REPO_DIR/wsgi/usntssearch/NZBmegasearch/
cp app.py $OPENSHIFT_REPO_DIR/

