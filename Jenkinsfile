pipeline {
    agent any 
    stages {
        stage('Build') {
            steps {
		cd client
		NODE_ENV=production npm install
		npm run build
		cp -rf dist ../src/server/static
            }
        }

	stage('Deploy') {
		zip -r dist.zip main.py requirements.txt src
		scp dist.zip orzo@dadescomunalts.tk
		ssh orzo@dadescomunalts.tk "sudo su; cd /opt/www/aps/hemeroteca-oberta; unzip -d /home/orzo/dist.zip .; bin/stopserver.sh && bin/runserver.sh --environment=PRO;"
	}
    }
}
