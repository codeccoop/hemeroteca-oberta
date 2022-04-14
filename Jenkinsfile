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
				'''
				stash(name: 'client-dist', includes: 'client/client.tar', useDefaultExcludes: true)
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
        			sh 'tar --strip-components=1 -C server/src/server/static -xvf client.tar'
					sh 'tar -cvf hemeroteca.tar server/main.py server/requierements.txt server/run.sh server/src'
					sh '''
						ls -ls server/src/static
						mkdir -p .ssh
                    	more ${KEY_FILE}
                    	cat ${KEY_FILE} > ./key_key.key
                    	eval $(ssh-agent -s)
                    	chmod 600 ./key_key.key
                    	ssh-add ./key_key.key
                    	scp -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" hemeroteca.tar orzo@192.168.10.130:hemeroteca.dist.tar
                    '''
				}
			}
		}
    }
}
