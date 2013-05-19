#~ OPENSHIFT_DATA_DIR
echo '*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*' 
echo '               NZBMEGASEARCH install for Openshift'
echo '*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*' 

echo 'Running update -- 01/02'
git fetch

echo 'Running update -- 02/02'
git reset --hard origin/master

echo 'Preparing...'
cp builtin_params.ini $OPENSHIFT_DATA_DIR
cp openshift/application .
cp openshift/app.py $OPENSHIFT_REPO_DIR/


cp -r $PWD $OPENSHIFT_REPO_DIR/wsgi

ctl_app restart
