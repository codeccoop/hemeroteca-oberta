pipeline {
	agent { dockerfile true }
	
	stages {
		stage('Build') {
			steps {
				sh '''
					cd client
					npm install
					npm run build
					tar -cvf client.tar dist
					mv client.tar ../client.tar
				'''
				stash(name: 'client-dist', includes: 'client.tar', useDefaultExcludes: true)
            }
        }

		stage('Deploy') {
			when {
            	expression {
                	currentBuild.result == null || currentBuild.result == 'SUCCESS' 
              	}
            }

			steps {
				withCredentials([sshUserPrivateKey(credentialsId: 'orzopad', keyFileVariable: 'KEY_FILE')]) {
					unstash 'client-dist'
					sh '''
						mkdir -p server/src/server/static
						tar --strip-components=1 -C server/src/server/static -xvf client.tar
						tar -cvf hemeroteca.tar server/main.py server/requirements.txt server/run.sh server/src

						mkdir -p .ssh
                    	more ${KEY_FILE}
                    	cat ${KEY_FILE} > ./key_key.key
                    	eval $(ssh-agent -s)
                    	chmod 600 ./key_key.key
                    	ssh-add ./key_key.key
						
                    	scp -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" hemeroteca.tar orzo@192.168.10.130:hemeroteca.tar
						ssh -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" orzo@192.168.10.130 << EOF
							cd /opt/www/apps/hemeroteca-oberta
							sudo tar -C $PWD --strip-components=1 -xvf $HOME/hemeroteca.tar
							if [ -d .venv ];
							then
								rm -rf .venv
							fi
							sudo virtualenv -p python3 .venv
							sudo .venv/bin/pip install -r requirements.txt

                            echo "Starting the server application"
							sudo ./run.sh
                            echo "Done"
						EOF
                    '''
				}
			}
		}
    }
}
