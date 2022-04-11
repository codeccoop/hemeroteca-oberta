pipeline {
	agent {
		docker { image 'ubuntu:20.04' }
	}
	
	stages {
		stage('Build') {
			steps {
				sh 'echo $PWD && ls -lh'
				sh 'cd client && NODE_ENV=production npm install && npm run build && cp -rf dist/* ../server/src/server/static'
            }
        }

		stage('Deploy') {
			steps {
				sh 'zip -r hemeroteca-oberta.zip main.py requirements.txt run.sh src'
				sh 'scp hemeroteca-oberta.zip orzo@192.168.10.130:hemeroteca-oberta.zip'
				sh 'ssh orzo@dadescomunals.org "sudo su; cd /opt/www/aps/hemeroteca-oberta; unzip /home/orzo/hemeroteca-oberta.zip -d .; kill $(cat process.pid); ./run.sh"'
			}
		}
    }
}