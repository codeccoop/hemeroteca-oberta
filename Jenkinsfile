pipeline {
	agent { dockerfile true }
	
	stages {
		stage('Build') {
			steps {
				sh 'node --version'
				// stash includes: './file', name: 'testfile'
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
					// unstash 'testfile'
					sh '''
						mkdir -p .ssh
                    	more ${KEY_FILE}
                    	cat ${KEY_FILE} > ./key_key.key
                    	eval $(ssh-agent -s)
                    	chmod 600 ./key_key.key
                    	ssh-add ./key_key.key
                    	ssh -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" orzo@192.168.10.130 cat /etc/hostname
                    '''
				}
			}
		}
    }
}
