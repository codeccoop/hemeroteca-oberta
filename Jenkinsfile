pipeline {
	agent {
		docker { image 'jenkins/agent:latest'}
	}
	
	stages {
		stage('Build') {
			steps {
				sh 'node --version'
				// stash includes: './file', name: 'testfile'
            }
        }

		stage('Deploy') {
			steps {
				// unstash 'testfile'
				sh 'echo $PWD && ls -lh'
				sh 'ssh orzo@192.168.10.130 "echo $HOSTNAME"'
				// sh 'cat ./file'
			}
		}
    }
}
